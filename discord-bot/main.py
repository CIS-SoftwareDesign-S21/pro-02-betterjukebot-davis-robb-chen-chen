import discord
import os
from discord.ext import commands
from secrets import DISCORD_TOKEN

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(
    brief="adds specified category",
    help="adds and enables specified category\nUsage: !load Memes",
)
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")


@bot.command(
    brief="removes specified category",
    help="removes and disables specified category\nUsage: !unload Memes",
)
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")


for filename in os.listdir("discord-bot/cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(DISCORD_TOKEN)
