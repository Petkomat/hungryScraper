from scraper import ScraperSelenium, Option
from helpers import create_logger
import re


LOGGER = create_logger(__file__)


class Vila(ScraperSelenium):
    def __init__(self, english: bool, only_today: bool):
        super().__init__(
            "Vila Teslova",
            "https://www.facebook.com/vilateslova/?locale=sl_SI",
            english,
            only_today,
            "🧚‍♀️"
        )

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
        LOGGER.info(f"Have {len(candidates)} candidates")
        for candidate in candidates:
            any_candidates = True
            done = self.try_add(ScraperSelenium.unescape(candidate))
            if done:
                break
            else:
                LOGGER.info("Candidate failure:", candidate)
        if not any_candidates:
            LOGGER.info("No candidates in\n", source)
        if not done:
            LOGGER.info("Did not find any menu")
        else:
            self.success = True

    def try_add(self, candidate: str):
        c_lower = candidate.lower()
        i_days = [(day, c_lower.find(day.lower())) for day in ScraperSelenium.DAYS.values()]
        present = [day for day, i in i_days if i >= 0]
        if not present:
            LOGGER.info(f"{candidate} contains no jedilnik")
            return False
        elif len(present) < 5:
            LOGGER.warning(f"Not all the days are present, but assuming this is still jedilnik: {candidate}")
        i_days.append(("sentinel", len(candidate)))
        for i, (day, i_day) in enumerate(i_days[:-1]):
            if i_day >= 0:
                description = candidate[i_day + len(day) + 1: i_days[i + 1][1]].strip()
                description = "\n".join(line.strip() for line in description.split("\n")) + "\n"
            else:
                description = "neznano"
            self.menus.append(Option(description, "morda neznana cena"))
        return True


if __name__ == "__main__":
    a = Vila(False, True)
    with open("vila.html", encoding="utf-8") as f:
        b = "".join(f.readlines())
    a._parse(b)
    print(a)
