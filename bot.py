import os
from discord.ext import commands
from dotenv import load_dotenv
from scraper_loncek import Loncek
from scraper_fe import FE
from scraper_vila import Vila
from scraper_mafija import Mafija
from scraper import Scraper
from helpers import create_logger
from typing import Union, List


LOGGER = create_logger(__file__)


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

LANGUAGES = {
    "sl": "si",
    "si": "si",
    "en": "en"
}
LOCATIONS = {
    "loncek": "loncek",
    "mafija": "mafija",
    "fe": "fe",
    "elektro": "fe",
    "vila": "vila"
}


SCRAPERS = {
    ("si", "today", "loncek"): Loncek(False, True),
    ("en", "today", "loncek"):  Loncek(True, True),
    ("si", "today", "fe"): FE(False, True),
    ("en", "today", "fe"): FE(True, True),
    ("si", "today", "vila"): Vila(False, True),
    ("en", "today", "vila"): Vila(True, True),
    ("si", "today", "mafija"): Mafija(False, True),
    ("en", "today", "mafija"): Mafija(True, True)
}


def get_menus(scrapers: List[Scraper]):
    for scraper in scrapers:
        scraper.get_menu()


async def send(
        ctx,
        scraper_s: Union[Scraper, List[Scraper]]
):
    scrapers = scraper_s if isinstance(scraper_s, list) else [scraper_s]
    LOGGER.info(f"Request for {[scraper.name for scraper in scrapers]}")
    get_menus(scrapers)
    message = "\n\n".join(str(scraper) for scraper in scrapers)
    max_size = 1500
    parts = list(range(0, len(message), max_size)) + [len(message)]
    last_message = None
    for i_part, i_start in enumerate(parts[:-1]):
        i_end = parts[i_part + 1]
        actual_message = message[i_start: i_end]
        if i_end != len(message):
            actual_message += "..."
        last_message = await ctx.send(actual_message)
    emojis = sorted({scraper.emoji for scraper in scrapers})
    if last_message is not None:
        for emoji in emojis:
            await last_message.add_reaction(emoji)


async def send_warning(ctx, warning):
    await ctx.send(warning)


def normalize_arguments(args: List[str]):
    normalized = []
    unknown = []
    for arg in args:
        if arg in LANGUAGES:
            normalized.append(LANGUAGES[arg])
        elif arg in LOCATIONS:
            normalized.append(LOCATIONS[arg])
        else:
            unknown.append(arg)
    return normalized, unknown


def get_location_lanugage(args: List[str]):
    location = "all"
    language = "all"
    for arg in args:
        if arg in LOCATIONS:
            location = arg
        elif arg in LANGUAGES:
            language = arg
    LOGGER.debug(f"{args} --> {location}, {language}")
    return location, language


def filter_scrapers(chosen_location, chosen_language):
    appropriate = []
    for (lan, _, loc), scraper in SCRAPERS.items():
        if chosen_language in ["all", lan] and chosen_location in ["all", loc]:
            appropriate.append(scraper)
    return appropriate


@bot.command(name="food")
async def handler(ctx, *args):
    normalized, unknown = normalize_arguments(args)
    if unknown:
        send_warning(
            ctx,
            f"There were some unknown arguments: {unknown}. "
            "Ignoring your command."
        )
        return
    loc, lan = get_location_lanugage(normalized)
    scrapers = filter_scrapers(loc, lan)
    await send(ctx, scrapers)


if __name__ == '__main__':
    get_menus(list(SCRAPERS.values()))
    bot.run(TOKEN)
