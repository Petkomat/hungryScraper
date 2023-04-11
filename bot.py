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


TODAY_SI_LONCEK = Loncek(False, True)
TODAY_EN_LONCEK = Loncek(True, True)
TODAY_SI_FE = FE(False, True)
TODAY_EN_FE = FE(True, True)
TODAY_SI_VILA = Vila(False, True)
TODAY_EN_VILA = Vila(True, True)
TODAY_SI_MAFIJA = Mafija(False, True)
TODAY_EN_MAFIJA = Mafija(True, True)


TODAY_SI = [TODAY_SI_LONCEK, TODAY_SI_FE, TODAY_SI_VILA, TODAY_SI_MAFIJA]
TODAY_EN = [TODAY_EN_LONCEK, TODAY_EN_FE, TODAY_EN_VILA, TODAY_EN_MAFIJA]

TODAY_LONCEK = [TODAY_SI_LONCEK, TODAY_EN_LONCEK]
TODAY_FE = [TODAY_SI_FE, TODAY_EN_FE]
TODAY_VILA = [TODAY_SI_VILA, TODAY_EN_VILA]
TODAY_MAFIJA = [TODAY_SI_MAFIJA, TODAY_EN_MAFIJA]

TODAY = TODAY_LONCEK + TODAY_FE + TODAY_VILA + TODAY_MAFIJA


def get_menus(scrapers: List[Scraper]):
    for scraper in scrapers:
        scraper.get_menu()


async def send(ctx, scraper_s: Union[Scraper, List[Scraper]]):
    scrapers = scraper_s if isinstance(scraper_s, list) else [scraper_s]
    LOGGER.info(f"Request for {[scraper.name for scraper in scrapers]}")
    get_menus(scrapers)
    message = "\n\n".join(str(scraper) for scraper in scrapers)
    max_size = 1500
    parts = list(range(0, len(message), max_size)) + [len(message)]
    for i_part, i_start in enumerate(parts[:-1]):
        i_end = parts[i_part + 1]
        actual_message = message[i_start: i_end]
        if i_end != len(message):
            actual_message += "..."
        await ctx.send(actual_message)


@bot.command(name='loncek-si')
async def loncek_si(ctx):
    await send(ctx, TODAY_SI_LONCEK)


@bot.command(name='loncek-en')
async def loncek_en(ctx):
    await send(ctx, TODAY_EN_LONCEK)


@bot.command(name='loncek')
async def loncek(ctx):
    await send(ctx, TODAY_LONCEK)


@bot.command(name='fe-si')
async def fe_si(ctx):
    await send(ctx, TODAY_SI_FE)


@bot.command(name='fe-en')
async def fe_en(ctx):
    await send(ctx, TODAY_EN_FE)


@bot.command(name='fe')
async def fe(ctx):
    await send(ctx, TODAY_FE)


@bot.command(name='vila-si')
async def vila_si(ctx):
    await send(ctx, TODAY_SI_VILA)


@bot.command(name='vila-en')
async def vila_en(ctx):
    await send(ctx, TODAY_EN_VILA)


@bot.command(name='vila')
async def vila(ctx):
    await send(ctx, TODAY_VILA)


@bot.command(name='mafija-si')
async def mafija_si(ctx):
    await send(ctx, TODAY_SI_MAFIJA)


@bot.command(name='mafija-en')
async def mafija_en(ctx):
    await send(ctx, TODAY_EN_MAFIJA)


@bot.command(name='mafija')
async def mafija(ctx):
    await send(ctx, TODAY_MAFIJA)


@bot.command(name='all-si')
async def all_si(ctx):
    await send(ctx, TODAY_SI)


@bot.command(name='all-en')
async def all_en(ctx):
    await send(ctx, TODAY_EN)


@bot.command(name='all')
async def all(ctx):
    await send(ctx, TODAY)


if __name__ == '__main__':
    get_menus(TODAY)
    bot.run(TOKEN)
