import os
from discord.ext import commands
from dotenv import load_dotenv
from scraper_loncek import Loncek
from scraper_fe import FE
from scraper_vila import Vila


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.command(name='loncek-si')
async def loncek_si(ctx):
    lonec = Loncek(False, True)
    lonec.get_menu()
    await ctx.send(str(lonec))


@bot.command(name='loncek-en')
async def loncek_en(ctx):
    lonec = Loncek(True, True)
    lonec.get_menu()
    await ctx.send(str(lonec))


@bot.command(name='fe-si')
async def fe_si(ctx):
    fe = FE(False, True)
    fe.get_menu()
    await ctx.send(str(fe))


@bot.command(name='fe-en')
async def fe_en(ctx):
    fe = FE(True, True)
    fe.get_menu()
    await ctx.send(str(fe))


@bot.command(name='vila-si')
async def vila_si(ctx):
    vila = Vila(False, True)
    vila.get_menu()
    await ctx.send(str(vila))


@bot.command(name='vila-en')
async def vila_en(ctx):
    vila = Vila(True, True)
    vila.get_menu()
    await ctx.send(str(vila))


bot.run(TOKEN)
