from bs4 import BeautifulSoup
from scraper import ScraperSoup, DailyMenu


class FE(ScraperSoup):
    DAYS = ["ponedeljek", "torek", "sreda", "četrtek", "petek"]

    def __init__(self, english: bool, only_today: bool):
        super().__init__('https://www.fe.uni-lj.si/o_fakulteti/restavracija/tedenski_meni/', english, only_today)

    def _parse(self, soup: BeautifulSoup):
        parsed_tables = {}
        for candidate in soup.find_all("h3"):
            day = ScraperSoup.get_string(candidate)
            if day not in FE.DAYS:
                continue
            parsed_table = []
            html_table = candidate.findNext("table")
            for html_row in html_table.find_all("tr"):
                parsed_row = []
                for html_cell in html_row.find_all("td"):
                    parsed_row.append(ScraperSoup.get_string(html_cell))
                parsed_table.append(parsed_row)
            parsed_tables[day] = parsed_table
        for day in FE.DAYS:
            if day not in parsed_tables:
                options = "nič"
            else:
                parsed_table = parsed_tables[day]
                daily_options = []
                for j in range(len(parsed_table[0])):
                    parts = [parsed_table[i][j] for i in range(1, len(parsed_table)) if parsed_table[i][j]]
                    daily_options.append(f"{parsed_table[0][j]}: {'; '.join(parts)}")
                options = "\n".join(daily_options)
            daily_menu = DailyMenu(options)
            self.menus.append(daily_menu)


if __name__ == "__main__":
    x = FE(False, True)
    x.get_menu()
    print(str(x))
