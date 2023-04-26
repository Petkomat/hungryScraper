from scraper import ScraperSelenium, Option
from helpers import create_logger
import re


LOGGER = create_logger(__file__)


class Vila(ScraperSelenium):
    SPECIAL_LINES = [
        "Stalna ponudba"
    ]

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
        We want to find a message whose text contains
        tedenski meni or ponedeljek ...

        "message": {
            ... ,
            "text": "Pozdravljeni!\nKako ste pa vi
                    za\u010deli teden? /.../
                    Tedenski meni 20.2. - 24.2.\nPonedeljek: ...
        }

        or "text": "Naša terasa je že /.../, do takrat pa imamo
                    tu tedenski meni (13.2. - 17.2.) Ponedeljek:
                    - Piščančji paprikaš s krompirjem, kruh ...
        :param source:
        :return:
        """
        done = False
        any_candidates = False
        candidates = re.findall(
            '"message": ?\\{[^}]+"text": ?"([^"}]+)"',
            source
        )
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
        day_matches = [
            Vila._extract_for_day(candidate, day)
            for day in ScraperSelenium.DAYS.values()
        ]
        present = [match for match in day_matches if match is not None]
        if not present:
            LOGGER.info(f"{candidate} contains no jedilnik")
            return False
        elif len(present) < 5:
            LOGGER.warning(
                "Not all the days are present, "
                f"but assuming this is still jedilnik: {candidate}"
            )
        everyday_offers = []
        for special in Vila.SPECIAL_LINES:
            match = Vila._extract_for_day(candidate, special)
            if match is not None:
                everyday_offers.append(match.group(1))
        additional_options = "\n".join(everyday_offers)
        for day_match in day_matches:
            if day_match is not None:
                description = day_match.group(1).strip()
                lines = [line.strip() for line in description.split("\n")]
                if additional_options:
                    lines.append(additional_options)
                description = "\n".join(lines) + "\n"
            else:
                description = "neznano"
            self.menus.append(Option(description, "morda neznana cena"))
        return True

    @staticmethod
    def _extract_for_day(candidate: str, start: str):
        stop_words = list(ScraperSelenium.DAYS.values())
        stop_words.extend(Vila.SPECIAL_LINES)
        stop = "|".join(stop_words)
        stop_pattern = f"(?:(?!{stop}).)*"
        if start in ScraperSelenium.DAYS.values():
            pattern = start + r":?\s*\n(" + stop_pattern + ")"
            flags = re.I | re.DOTALL
        else:
            pattern = "(" + start + r":?" + stop_pattern + ")"
            flags = re.I
        return re.search(pattern, candidate, flags=flags)


if __name__ == "__main__":
    a = Vila(False, True)
    with open("vila.html", encoding="utf-8") as f:
        b = "".join(f.readlines())
    a._parse(b)
    print(a)
