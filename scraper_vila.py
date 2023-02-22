from scraper import ScraperSelenium, Option
import re


class Vila(ScraperSelenium):
    def __init__(self, english: bool, only_today: bool):
        super().__init__("https://www.facebook.com/vilateslova/?locale=sl_SI", english, only_today)

    def _parse(self, source: str):
        """
        We want to find a message whose text contains tedenski meni or ponedeljek ...

        "message": {... , "text": "Pozdravljeni!\nKako ste pa vi za\u010deli teden? /.../ Tedenski meni 20.2. - 24.2.\nPonedeljek: ... }

        or "text": "Naša terasa je že /.../, do takrat pa imamo tu tedenski meni (13.2. - 17.2.) Ponedeljek:
            - Piščančji paprikaš s krompirjem, kruh ...
        :param source:
        :return:
        """
        done = False
        any_candidates = False
        candidates = re.findall('"message": ?\\{[^}]+"text": ?"([^"}]+)"', source)
        print(f"Have {len(candidates)} candidates")
        for candidate in candidates:
            any_candidates = True
            done = self.try_add(ScraperSelenium.unescape(candidate))
            if done:
                break
            else:
                print("Candidate failure:", candidate)
        if not any_candidates:
            print("No candidates in\n", source)
        if not done:
            print("Did not find any menu")
        else:
            self.success = True

    def try_add(self, candidate: str):
        c_lower = candidate.lower()
        i_days = [(day, c_lower.find(day.lower())) for day in ScraperSelenium.DAYS.values()]
        if min([i for _, i in i_days]) < 0:
            print(candidate, "contains no jedilnik")
            return False
        i_days.append(("sentinel", len(candidate)))
        for i, (day, i_day) in enumerate(i_days[:-1]):
            description = candidate[i_day + len(day) + 1: i_days[i + 1][1]].strip()
            description = "\n".join(line.strip() for line in description.split("\n")) + "\n"
            self.menus.append(Option(description, "NEZNANE CENE"))
        return True


if __name__ == "__main__":
    a = Vila(False, True)
    with open("vila.html", encoding="utf-8") as f:
        b = "".join(f.readlines())
    a._parse(b)
    print(a)
