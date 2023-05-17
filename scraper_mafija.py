from scraper import ScraperSoup, Option, DailyMenu
from bs4 import BeautifulSoup
from helpers import create_logger
from datetime import date
import re


LOGGER = create_logger(__file__)


class Mafija(ScraperSoup):
    EVERYDAY = ["TORTILJA", "SENDVIČ", "SOLATA"]
    TODAY_BUTTON_CLASS = (
        "btn btn-sm btn-default rounded margin-right-5 "
        "margin-bottom-5 menu-request-link disabled btn-info"
    )

    def __init__(self, english: bool, only_today: bool):
        if not only_today:
            raise ValueError(
                "Menu for the whole week is not accessible. " "Set only_today to True"
            )
        super().__init__(
            "Mafija",
            "https://www.studentska-prehrana.si/sl/restaurant/Details/2993",
            english,
            only_today,
            "🔫",
        )
        self.today = -1

    def _has_menu(self):
        return Mafija.index_of_today() == self.today

    def get_menu(self):
        super().get_menu()
        self.today = Mafija.index_of_today()

    def _parse(self, soup: BeautifulSoup):
        # simulate whole week
        self.menus = [DailyMenu("neznano") for _ in range(5)]
        i_today = Mafija.index_of_today()
        if i_today >= len(self.menus):
            return
        everyday: list[tuple[str, str]] = []
        todays_specialty: list[str] = []
        date_html = soup.find("a", class_=Mafija.TODAY_BUTTON_CLASS)
        date_str = date_html.get("onclick")
        if not Mafija._is_today(date_str):
            return
        for option in soup.find_all("p", class_="text-bold color-blue"):
            description_raw = ScraperSoup.get_string(option)
            description = re.search(r"(\d+ )?(.+)", description_raw).group(2).strip()

            generic_word: str | None = None
            for generic in Mafija.EVERYDAY:
                if generic.lower() in description.lower():
                    generic_word = generic
                    break
            if generic_word is not None:
                everyday.append((generic_word, description))
            else:
                todays_specialty.append(description)
        everyday.sort()
        if not todays_specialty:
            LOGGER.warning(f"No specialty among {everyday}")
        elif len(todays_specialty) > 1:
            LOGGER.warning(f"More than one specialty: {todays_specialty}")

        parsed_daily = "; ".join(todays_specialty).lower() if todays_specialty else "neznano"
        parsed_every_day = "; ".join(option for _, option in everyday).lower()
        the_daily_option = Option(
            f"  - Dnevna ponudba: {parsed_daily}", price="neznana cena"
        )
        everyday_options = Option(
            f"  - Ostalo: {parsed_every_day}", price="razne cene"
        )
        this_day_options = DailyMenu(
            "\n".join([str(the_daily_option), str(everyday_options)])
        )
        i_today = Mafija.index_of_today()
        self.menus[i_today] = this_day_options

    @staticmethod
    def _is_today(date_str: str):
        today = date.today()
        d_m_y = today.day, today.month, today.year
        pattern = r"'(\d+)[. ]+(\d+)[. ]+(\d{4})"
        m = re.search(pattern, date_str)
        if m is None:
            LOGGER.warning(f"Weird date format: {date_str}")
            return False
        d_m_y_menu = tuple(int(m.group(i)) for i in range(1, 4))
        return d_m_y == d_m_y_menu


if __name__ == "__main__":
    a = Mafija(True, True)
    a.get_menu()
    print(a)
    a = Mafija(False, True)
    a.get_menu()
    print(a)
