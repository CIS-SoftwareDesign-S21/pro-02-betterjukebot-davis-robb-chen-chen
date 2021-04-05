import discord
from discord import Client
from discord.ext import commands
from discord.ext import tasks
import os
import youtube_dl
from secrets import DISCORD_TOKEN

# Creating the Bot
bot = discord.Client()
bot = commands.Bot(command_prefix="!")
global channel_default
channel_default = "General"


@bot.event
async def on_ready():
    print("Connected to bot: {}".format(bot.user.name))
    print("Bot ID: {}".format(bot.user.id))


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
async def angry(ctx):
    await ctx.send(":angry:")

@bot.command()
async def repeat(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
    voice.play(discord.FFmpegPCMAudio("song.mp3"))


@bot.command()
async def seek(ctx, timestamp: int):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
    voice.play(
        discord.FFmpegPCMAudio(
            source="song.mp3",
            executable="ffmpeg",
            pipe=False,
            stderr=None,
            before_options=None,
            options="-ss " + str(timestamp),
        )
    )


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

    print(channel_default)
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=channel_default)
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
    voice.play(discord.FFmpegPCMAudio("song.mp3"))


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


@bot.command()
async def joinchannel(ctx, channel: str):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=channel)
    await voiceChannel.connect()


@bot.command()
async def create(ctx, channel: str):
    guild = ctx.message.guild

    await guild.create_voice_channel(channel)
    await ctx.send("Channel created")


@bot.command()
async def remove(ctx, channel: str):
    existing_channel = discord.utils.get(ctx.guild.channels, name=channel)

    if existing_channel is not None:
        await existing_channel.delete()
    else:
        await ctx.send(f'No channel named "{channel}" was found')


@bot.command()
async def setchannel(ctx, channel: str):
    existing_channel = discord.utils.get(ctx.guild.channels, name=channel)
    global channel_default

    if existing_channel is not None:
        channel_default = channel
        await ctx.send(f'set default playing channel to "{channel}"')
    else:
        await ctx.send(f'No channel named "{channel}" was found')
        await ctx.send("Please create the channel first")

    print(channel_default)


@tasks.loop(seconds = 10)
async def idle_channel():
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        member_count = len(voice.members)
        if member_count == 1:
            await voice.disconnect()

idle_channel.start()

# Running the bot
bot.run(DISCORD_TOKEN)
