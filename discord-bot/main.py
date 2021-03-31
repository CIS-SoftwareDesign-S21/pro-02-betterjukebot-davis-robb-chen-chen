import discord
from discord.ext import commands
import os
import youtube_dl
import bandcamp_dl
import urllib.parse

# Credentials
TOKEN = "ODIzNDI0MjQ3ODYyMDAxNjY0.YFgnlw.VZk0hl3tb9iYhNb1I0AdVgvcUqI"

# Creating the Bot
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Connected to bot: {}".format(bot.user.name))
    print("Bot ID: {}".format(bot.user.id))


# Command


@bot.command()
async def hello_world(ctx):
    await ctx.send("Hello World!")


@bot.command()
async def soup(ctx):
    await ctx.send("Soup!")


@bot.command()
async def goober(ctx):
    await ctx.send("Becca")


@bot.command()
async def youtube(ctx, *, search):
    await ctx.send("Doing youtube searches soon")


@bot.command()
async def seek(ctx, timestamp: int):
    await ctx.send("Doing seeking soon")


@bot.command()
async def play(ctx, url: str):
    song = os.path.isfile("song.mp3")
    try:
        if song:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send(
            "Cannot play another song until song currently playing is complete"
        )
        return

    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name="General")
    await voiceChannel.connect()
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")



@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not in a channel.")



@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Nothing is playing.")


@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Voice is not paused")


# Running the bot
bot.run(TOKEN)
