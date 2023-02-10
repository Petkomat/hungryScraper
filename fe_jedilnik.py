import sys
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import ssl
from datetime import timedelta, date
import translators as ts
import translators.server as tss

# TODO :)


class DailyMenu:
    def __init__(self, english):
        self.english = english

    def __str__(self):
        soup = self.soup['soup'] if not self.english else tss.google(self.soup['soup'], 'sl', 'en')
        menu = f"{self.day}\n------------\n{'Soup' if self.english else 'Juha'}: {soup}\n"
        for id, menu_item in enumerate(self.menu):
            if self.english and menu_item:
                menu_item = tss.google(menu_item, 'sl', 'en')
            menu += f"Menu {id+1}: {menu_item}\n"
        return menu


def main(english=False):
    gcontext = ssl.SSLContext()  # Only for gangstars
    req = Request(
        url='https://www.fe.uni-lj.si/o_fakulteti/restavracija/tedenski_meni/'
    )
    webpage = urlopen(req, context=gcontext).read()
    print()
    soup = BeautifulSoup(webpage, 'html.parser')
    items = []
    menus = [DailyMenu(english) for _ in range(5)]
    today = date.today()
    menus[0].day = ("Monday " if english else "Ponedeljek ") + str(today)
    menus[1].day = ("Tuesday " if english else "Torek ") + str(today + timedelta(days=1))
    menus[2].day = ("Wednesday " if english else "Sreda ") + str(today + timedelta(days=2))
    menus[3].day = ("Thursday " if english else "Četrtek ") + str(today + timedelta(days=3))
    menus[4].day = ("Friday " if english else "Petek ") + str(today + timedelta(days=4))

    day = 0
    for table in soup.find_all('table'):
        rows = list(table.find_all('tr'))
        menus[day].soup = { 'soup' : rows[1].td.p.string }
        daily_menus = ['' for _ in range(7)]
        for idx, menu in enumerate(rows[2].find_all('td')):
            menu_desc = ''
            for item in menu.find_all('p'):
                menu_desc += item.string + " "
            daily_menus[idx] += menu_desc.strip()
        for idx, menu in enumerate(rows[3].find_all('td')):
            menu_desc = ''
            for item in menu.find_all('p'):
                if item.string:
                    menu_desc += item.string
                daily_menus[idx] += ", " + menu_desc
        menus[day].menu = daily_menus
        day += 1
    for menu in menus:
        print(menu)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--en":
        main(english=True)
    else:
        main(False)
