import os
from discord.ext import commands
from dotenv import load_dotenv
from scraper_loncek import Loncek

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.command(name='loncek-si')
async def loncek(ctx):
    lonec = Loncek(False, True)
    lonec.get_menu()
    await ctx.send(str(lonec))


@bot.command(name='loncek-en')
async def loncek(ctx):
    lonec = Loncek(True, True)
    lonec.get_menu()
    await ctx.send(str(lonec))


@bot.command(name='fe-slo')
async def loncek(ctx):
    response = "Ne znam praskati po FE"
    await ctx.send(response)


bot.run(TOKEN)

