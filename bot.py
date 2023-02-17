import os
from discord.ext import commands
from dotenv import load_dotenv
from scraper_loncek import Loncek
from scraper_fe import FE


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


bot.run(TOKEN)

