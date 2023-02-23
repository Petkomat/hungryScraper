from scraper import ScraperSoup, Option, DailyMenu
from bs4 import BeautifulSoup


class Loncek(ScraperSoup):
    def __init__(self, english: bool, only_today: bool):
        super().__init__("Lonček", 'https://loncek-kuhaj.si/tedenski-jedilnik-tp.php', english, only_today)

    def _parse(self, soup: BeautifulSoup):
        daily_options = []
        for candidate in soup.find_all(class_='pm-menu-item-desc'):
            titles = candidate.find_all(class_='pm-menu-item-title')
            excerpts = candidate.find_all(class_='pm-menu-item-excerpt')
            prices = candidate.find_all(class_='pm-menu-item-price')
            if len(titles) != 1 or len(excerpts) != 1 or len(prices) > 1:
                # print(f"Skipping:\n{candidate}")
                continue
            title = ScraperSoup.get_string(titles[0])
            excerpt = ScraperSoup.get_string(excerpts[0])
            price = ScraperSoup.get_string(prices[0]) if prices else ""
            if title and (not excerpt or not price):
                # (Zaprto, "", "2 €") or (Dnevna juha, Goveja, "")
                daily_options.append([])
            description = Loncek.get_menu_description(title, excerpt)
            daily_options[-1].append(Option(description, price))
        if len(daily_options) != 5:
            raise ValueError(f"Found {len(daily_options)} options: {daily_options}")
        for group in daily_options:
            self.menus.append(DailyMenu("\n".join(str(x) for x in group)))

    @staticmethod
    def get_menu_description(title: str, excerpt: str):
        if title and excerpt:
            description = f"{title}: {excerpt}"
        elif title:
            description = title
        elif excerpt:
            description = excerpt
        else:
            description = "nič"
        return description


if __name__ == "__main__":
    a = Loncek(False, False)
    a.get_menu()
    print(a)
    a = Loncek(False, True)
    a.get_menu()
    print(a)

    a = Loncek(True, False)
    a.get_menu()
    print(a)
