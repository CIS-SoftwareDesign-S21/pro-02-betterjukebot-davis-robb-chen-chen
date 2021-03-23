import discord
from discord.ext import commands

# Credentials
TOKEN = "ODIzNDI0MjQ3ODYyMDAxNjY0.YFgnlw.VZk0hl3tb9iYhNb1I0AdVgvcUqI"

# Creating the Bot
client = commands.Bot(command_prefix="!")


@client.event
async def on_ready():
    print("Connected to bot: {}".format(client.user.name))
    print("Bot ID: {}".format(client.user.id))


# Command


@client.command()
async def hello_world(ctx):
    await ctx.send("Hello World!")


# Running the bot
client.run(TOKEN)