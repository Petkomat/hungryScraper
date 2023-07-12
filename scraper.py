import re
from datetime import date, timedelta
import os
import traceback

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import translators.server as tss

from selenium import webdriver
from selenium.webdriver import Chrome, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from helpers import create_logger


LOGGER = create_logger(__file__)


class Option:
    def __init__(self, description: str, price: str):
        self.description = description
        self.price = price

    def __str__(self):
        price = self.price if self.price else "-"
        return f"{self.description} ({price})"


class DailyMenu:
    def __init__(self, description: str):
        self.description = description

    def __str__(self):
        return self.description


class Scraper:
    DAYS = {
        "Monday": "Ponedeljek",
        "Tuesday": "Torek",
        "Wednesday": "Sreda",
        "Thursday": "Četrtek",
        "Friday": "Petek"
    }

    def __init__(
            self,
            name: str,
            url: str,
            english: bool,
            only_today: bool,
            emoji: str
    ):
        self.name = name
        self.url = url
        self.english = english
        self.only_today = only_today
        self.emoji = emoji
        self.monday = Scraper.this_monday()
        self.menus: list[DailyMenu] = []

    @staticmethod
    def this_monday():
        today = date.today()
        return today - timedelta(days=today.weekday())

    @staticmethod
    def index_of_today():
        return date.today().weekday()

    def __str__(self) -> str:
        parts: list[str] = []
        for days_delta, daily_menu in enumerate(self.menus):
            today = self.monday + timedelta(days=days_delta)
            if self.only_today and today != date.today():
                continue
            weekday = Scraper.DAYS[today.strftime("%A")]
            parts.append(
                f"{weekday} ({today.day}. {today.month}. {today.year})"
            )
            parts.append(str(daily_menu))
            parts.append("\n")
        if parts:
            parts.pop()
        everything = "\n\n".join(parts)
        if self.english and everything:
            for _ in range(10):
                try:
                    everything = tss.google(everything, 'sl', 'en')
                    time.sleep(1.0)
                    break
                except TypeError:
                    LOGGER.error(traceback.format_exc())
        raw = f"**{self.name}** {self.emoji}:\n{everything}"
        return Scraper._postprocess_str(raw)
    
    @staticmethod
    def _postprocess_str(raw: str) -> str:
        """
        Takes care of discord peculiarities in formatting. For now, it
        - removes any space between newline characters and dashes.
        - adds a space after a dash, if the dash is preceded by a newline character.
        """
        better = re.sub(r"\n\s+-", "\n- ", raw)
        better = re.sub(r"\n-\s*", "\n- ", better)
        return better

    def _get_menu(self) -> None:
        raise NotImplementedError()

    def _has_menu(self):
        return self.monday == Scraper.this_monday() and self.menus

    def get_menu(self):
        if not self._has_menu():
            self.menus = []
            try:
                self._get_menu()
            except:
                LOGGER.error(traceback.format_exc())
                self.menus = [DailyMenu(f"Nisem mogel prebaviti, obišči {self.url}") for _ in range(5)]
            self.monday = Scraper.this_monday()


class ScraperSoup(Scraper):
    def __init__(
            self,
            name: str,
            url: str,
            english: bool,
            only_today: bool,
            emoji: str
    ):
        super().__init__(name, url, english, only_today, emoji)

    def _get_soup(self):
        req = Request(url=self.url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        return BeautifulSoup(webpage, 'html.parser')

    def _get_menu(self):
        soup = self._get_soup()
        self._parse(soup)

    def _parse(self, soup: BeautifulSoup):
        raise NotImplementedError()

    @staticmethod
    def get_string(html_element) -> str:
        text = html_element.text.replace("\n", " ").replace("\t", " ")
        return re.sub(" +", " ", text).strip()


class ScraperSelenium(Scraper):
    def __init__(
            self,
            name: str,
            url: str,
            english: bool,
            only_today: bool,
            emoji: str
    ):
        super().__init__(name, url, english, only_today, emoji)
        self.success = False

    def __str__(self):
        if self.success:
            return super().__str__()
        elif self.english:
            return f"No success with parsing. Visit {self.url}"
        else:
            return f"Nisem mogel dobiti menija. Obišči {self.url}"

    def _get_source(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        chrome_path = ChromeDriverManager().install()
        chrome_service = Service(chrome_path)
        driver = Chrome(options=options, service=chrome_service)
        driver.implicitly_wait(5)
        driver.get(self.url)
        html = driver.find_element(By.TAG_NAME, 'html')
        html.send_keys(Keys.END)
        time.sleep(2)
        return driver.page_source

    def _get_menu(self):
        source = self._get_source()
        self._parse(source)

    def _parse(self, source: str):
        raise NotImplementedError()

    @staticmethod
    def unescape(source: str):
        parts: list[str] = []
        i = 0
        fake_file = open(os.devnull, "w", encoding="utf-8")
        while i < len(source):
            character = source[i]
            if character == '\\':
                next_character = source[i + 1]
                if next_character == "n":
                    parts.append("\n")
                    i += 2
                elif next_character == "t":
                    parts.append("\t")
                    i += 2
                elif next_character == "u":
                    code = source[i + 2: i + 6]
                    try:
                        c = chr(int(code, 16))
                        print(c, file=fake_file)
                        parts.append(c)
                    except UnicodeEncodeError:
                        print(
                            f"Cannot decode source[{i + 2}:{i + 6}] = {code} "
                            "as a single character (probably emoticon?)"
                        )
                    i += 6
                else:
                    raise ValueError(
                        "Unexpected continuation after \\: "
                        f"{source[i + 1: i + 10]}"
                    )
            else:
                parts.append(character)
                i += 1
        fake_file.close()
        return "".join(parts)
