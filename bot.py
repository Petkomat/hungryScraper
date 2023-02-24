import os
from discord.ext import commands
from dotenv import load_dotenv
from scraper_loncek import Loncek
from scraper_fe import FE
from scraper_vila import Vila
from scraper import Scraper
from typing import Callable


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


async def send_single(ctx, s: Callable[[bool, bool], Scraper], english: bool, only_today: bool):
    scraper = s(english, only_today)
    scraper.get_menu()
    await ctx.send(str(scraper))


async def send_all(ctx, english):
    loncek = Loncek(english, True)
    fe = FE(english, True)
    vila = Vila(english, True)
    all_locations = [loncek, fe, vila]
    for location in all_locations:
        location.get_menu()
    await ctx.send("\n\n".join(str(location) for location in all_locations))


@bot.command(name='loncek-si')
async def loncek_si(ctx):
    await send_single(ctx, Loncek, False, True)


@bot.command(name='loncek-en')
async def loncek_en(ctx):
    await send_single(ctx, Loncek, True, True)


@bot.command(name='fe-si')
async def fe_si(ctx):
    await send_single(ctx, FE, False, True)


@bot.command(name='fe-en')
async def fe_en(ctx):
    await send_single(ctx, FE, True, True)


@bot.command(name='vila-si')
async def vila_si(ctx):
    await send_single(ctx, Vila, False, True)


@bot.command(name='vila-en')
async def vila_en(ctx):
    await send_single(ctx, Vila, True, True)


@bot.command(name='all-si')
async def all_si(ctx):
    await send_all(ctx, False)


@bot.command(name='all-en')
async def all_en(ctx):
    await send_all(ctx, True)


bot.run(TOKEN)
