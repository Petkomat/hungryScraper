from bs4 import BeautifulSoup
from scraper import ScraperSoup, DailyMenu
from helpers import create_logger


LOGGER = create_logger(__file__)


class FE(ScraperSoup):
    DAYS = ["ponedeljek", "torek", "sreda", "četrtek", "petek"]

    def __init__(self, english: bool, only_today: bool):
        super().__init__(
            "FE",
            'https://www.fe.uni-lj.si/o_fakulteti/restavracija/tedenski_meni/',
            english,
            only_today,
            "⚡"
        )

    def _parse(self, soup: BeautifulSoup):
        for candidate in soup.find_all("div", class_="accordion-single"):
            day_all = ScraperSoup.get_string(candidate.find("h2"))
            day = FE._extract_day(day_all)
            if day is None:
                day = FE.DAYS[len(self.menus)]
                LOGGER.warning(f"No idea, which day is this: {day_all}, assuming {day}")
            options: list[str] = []
            for html_menu in candidate.find_all("li"):
                option = ScraperSoup.get_string(html_menu)
                options.append(f"  - {option}")
            daily_menu = DailyMenu("\n".join(options))
            self.menus.append(daily_menu)

    @staticmethod
    def _extract_day(day_string: str) -> str | None:
        day_string = day_string.lower()
        for day in FE.DAYS:
            if day_string.startswith(day.lower()):
                return day
        return None


if __name__ == "__main__":
    x = FE(False, False)
    x._get_menu()
    print(str(x))
