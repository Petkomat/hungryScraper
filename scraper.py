from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import date, timedelta
import translators.server as tss
import re


DAYS = {
    "Monday": "Ponedeljek",
    "Tuesday": "Torek",
    "Wednesday": "Sreda",
    "Thursday": "Četrtek",
    "Friday": "Petek"
}


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
            weekday = DAYS[actual_date.strftime("%A")]
            parts.append(f"{weekday} ({actual_date.day}. {actual_date.month}. {actual_date.year})")
            parts.append(str(daily_menu))
            parts.append("\n")
        everything = "\n".join(parts)
        if self.english:
            everything = tss.google(everything, 'sl', 'en')
        return everything

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
