import re
from datetime import date, timedelta
import os

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import translators.server as tss

from selenium import webdriver
from selenium.webdriver import Chrome, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time


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

    def __init__(self, url: str, english: bool, only_today: bool):
        self.url = url
        self.english = english
        self.only_today = only_today
        self.monday = Scraper.this_monday()
        self.menus = []

    @staticmethod
    def this_monday():
        today = date.today()
        return today - timedelta(days=today.weekday())

    def __str__(self):
        parts = []
        for days_delta, daily_menu in enumerate(self.menus):
            actual_date = self.monday + timedelta(days=days_delta)
            if self.only_today and actual_date != date.today():
                continue
            weekday = Scraper.DAYS[actual_date.strftime("%A")]
            parts.append(f"{weekday} ({actual_date.day}. {actual_date.month}. {actual_date.year})")
            parts.append(str(daily_menu))
            parts.append("\n")
        everything = "\n".join(parts)
        if self.english:
            everything = tss.google(everything, 'sl', 'en')
        return everything

    def get_menu(self):
        raise NotImplementedError()


class ScraperSoup(Scraper):
    def __init__(self, url: str, english: bool, only_today: bool):
        super().__init__(url, english, only_today)

    def _get_soup(self):
        req = Request(url=self.url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        return BeautifulSoup(webpage, 'html.parser')

    def get_menu(self):
        soup = self._get_soup()
        self._parse(soup)

    def _parse(self, soup: BeautifulSoup):
        raise NotImplementedError()

    @staticmethod
    def get_string(html_element):
        text = html_element.text.replace("\n", " ").replace("\t", " ")
        return re.sub(" +", " ", text).strip()


class ScraperSelenium(Scraper):
    def __init__(self, url: str, english: bool, only_today: bool):
        super().__init__(url, english, only_today)
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

    def get_menu(self):
        source = self._get_source()
        self._parse(source)

    def _parse(self, source: str):
        raise NotImplementedError()

    @staticmethod
    def unescape(source: str):
        parts = []
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
                            f"Cannot decode source[{i + 2}:{i + 6}] = {code} as a single character (probably emoticon?)"
                        )
                    i += 6
                else:
                    raise ValueError(f"Unexpected continuation after \\: {source[i + 1: i + 10]}")
            else:
                parts.append(character)
                i += 1
        fake_file.close()
        return "".join(parts)