import discord
from discord.ext import commands
import os
import asyncio
import youtube_dl
# import musixmatch
from secrets import DISCORD_TOKEN

# Creating the Bot
bot = discord.Client()
bot = commands.Bot(command_prefix="!")
global channel_default
channel_default = "General"
global created_channels
created_channels = []

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
async def angryarray(ctx):
    await ctx.send(":angry::rage::angry:\n:rage::angry::rage:""\n:angry::rage::angry:")


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

    # checks for idle channel
    while voice.is_playing():
        await asyncio.sleep(1)
    else:
        await asyncio.sleep(15)
        while voice.is_playing():
            break
        else:
            await voice.disconnect()
            for created in created_channels:
                if voiceChannel == created:
                    await voiceChannel.delete()


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

    global created_channels
    created_channels.append(discord.utils.get(ctx.guild.channels, name=channel))


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
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    global channel_default

    if existing_channel is not None and voice.is_playing():
        channel_default = channel
        await voice.pause
        await voice.disconnect
        await existing_channel.connect
        await ctx.send(f'switching playing channel to "{channel}"')
    elif existing_channel is not None and not voice.is_playing():
        channel_default = channel
        await ctx.send(f'set default playing channel to "{channel}"')
    else:
        await ctx.send(f'No channel named "{channel}" was found')
        await ctx.send("Please create the channel first")

    print(channel_default)


# Running the bot
bot.run(DISCORD_TOKEN)
