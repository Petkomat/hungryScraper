from scraper import ScraperSoup, Option, DailyMenu
from bs4 import BeautifulSoup


class Mafija(ScraperSoup):
    def __init__(self, english: bool, only_today: bool):
        if not only_today:
            raise ValueError("Menu for the whole week is not accessible. Set only_today to True")
        super().__init__("Mafija", 'https://www.studentska-prehrana.si/sl/restaurant/Details/2993', english, only_today)
        self.today = -1

    def _has_menu(self):
        return Mafija.index_of_today() == self.today

    def get_menu(self):
        super().get_menu()
        self.today = Mafija.index_of_today()

    def _parse(self, soup: BeautifulSoup):
        parsed_daily = "nekaj danes"  # TODO Sparsaj soup za tole
        parsed_every_day = ["sendviči", "tortilje", "solate"]  # lahko tudi to :)
        the_daily_option = Option(f"Dnevna ponudba: {parsed_daily}", price="neznana cena")
        everyday_options = Option(f"Ostalo: {'; '.join(parsed_every_day)}", price="razne cene")
        this_day_options = DailyMenu("\n".join([str(the_daily_option), str(everyday_options)]))
        # simulate whole week
        self.menus = [DailyMenu("neznano") for _ in range(5)]
        i_today = Mafija.index_of_today()
        if i_today < len(self.menus):
            self.menus[i_today] = this_day_options


if __name__ == "__main__":
    a = Mafija(True, True)
    a.get_menu()
    a.get_menu()
    print(a)
    a = Mafija(False, True)
    a.get_menu()
    print(a)
