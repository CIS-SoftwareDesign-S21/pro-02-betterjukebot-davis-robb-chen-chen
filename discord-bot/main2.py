import discord
import os
from discord.ext import commands
from secrets import DISCORD_TOKEN

bot = commands.Bot(command_prefix="!")


@bot.command(brief="adds specified category", help="adds and enables specified category\nUsage: !load Memes")
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")


@bot.command(brief="removes specified category", help="removes and disables specified category\nUsage: !unload Memes")
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")


@bot.command(brief="prints 'hello_world'", help="prints 'hello_world' our minimal project")
async def hello_world(ctx):
    await ctx.send("Hello World!")


@bot.command(brief="prints 'soup!'", help="prints 'soup!' as a Ju-Hung test ")
async def soup(ctx):
    await ctx.send("Soup!")


@bot.command(brief="prints 'Becca'", help="prints 'Becca' as a Becca test")
async def goober(ctx):
    await ctx.send("Becca")


@bot.command(brief="prints ':angry:'", help="angry emoji command prints ':angry:'")
async def angry(ctx):
    await ctx.send(":angry:")


@bot.command(brief="prints ':angry::rage: array'", help="angryarray emoji command prints ':angry::rage: array'")
async def angryarray(ctx):
    await ctx.send(":angry::rage::angry:\n:rage::angry::rage:" "\n:angry::rage::angry:")


for filename in os.listdir("discord-bot/cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(DISCORD_TOKEN)
