import discord
from discord.ext.commands import Bot
import os
import asyncio
import youtube_dl

from secrets import DISCORD_TOKEN, MUSIXMATCH_TOKEN

from musixmatch import Musixmatch
musixmatch = Musixmatch(MUSIXMATCH_TOKEN)

# Creating the Bot
bot = Bot(command_prefix="!")
global channel_default
channel_default = "general"
global created_channels
created_channels = []
global idle_timer
idle_timer = 300  # seconds (default 5 minutes)
global display_lyrics
display_lyrics = True


@bot.event
async def on_ready():
    print("Connected to bot: {}".format(bot.user.name))
    print("Bot ID: {}".format(bot.user.id))


# @bot.event
# async def on_voice_state_update(member, before, after):
#    if after.voice.channel is not None:
#        if after.voice.channel.name == "general":
#            print("The event is working")


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
    await ctx.send(":angry::rage::angry:\n:rage::angry::rage:" "\n:angry::rage::angry:")


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
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    print(voiceChannel)
    if voice == None:
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

    # idle check
    global idle_timer
    while voice.is_playing() and len(
            voiceChannel.members) is not 1:  # checks if bot is playing music/if bot alone in voice
        await asyncio.sleep(1)
    else:
        await asyncio.sleep(idle_timer)
        while voice.is_playing() and len(voiceChannel.members) is not 1:
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
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    guild = ctx.message.guild

    if voiceChannel is None:
        await guild.create_voice_channel(channel)
        await ctx.send(f'Created channel "{channel}"')

    if voice.is_playing():
        voice.pause()
        await voice.disconnect()
        await voiceChannel.connect()
        voice.resume()
        await ctx.send(f'switching playing channel to "{channel}"')
    else:
        await voiceChannel.connect()
        await ctx.send(f'Joined channel "{channel}"')


@bot.command()
async def create(ctx, channel: str):
    guild = ctx.message.guild
    existing_channel = discord.utils.get(ctx.guild.channels, name=channel)

    if existing_channel is None:
        await guild.create_voice_channel(channel)
        await ctx.send("Channel created")
        global created_channels
        created_channels.append(discord.utils.get(ctx.guild.channels, name=channel))
    else:
        await ctx.send(f'Channel "{channel}" already exists')


@bot.command()
async def remove(ctx, channel: str):
    channel = discord.utils.get(ctx.guild.channels, name=channel)
    channel_members = bot.get_channel(channel.id).members

    if channel is not None and not channel_members:
        await ctx.send(f'Are you sure you want to delete channel "{channel}"? (y or n)')

        # below are requirements for user input, if not y or n will not accept the input
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ["y", "n"]

        msg = await bot.wait_for("message", check=check)  # waits for user input y or n
        if msg.content.lower() == "y":
            await channel.delete()
            await setchannel(ctx, "general")
            print(channel_members)
            print(channel)
        else:
            await ctx.send("Cancelling...")
            print("Remove cancelled.")
    else:
        await ctx.send(f'Channel "{channel}" does not exist or has member(s) inside')
        print(channel_members)
        print(channel)


@bot.command()
async def setchannel(ctx, channel: str):
    existing_channel = discord.utils.get(ctx.guild.channels, name=channel)
    guild = ctx.message.guild
    global channel_default

    if existing_channel is not None:
        channel_default = channel
        await ctx.send(f'set default playing channel to "{channel}"')
        print(channel_default)
        await joinchannel(ctx, channel)
    else:
        channel_default = channel
        await guild.create_voice_channel(channel)
        await ctx.send("Channel created and set to default playing channel")
        await joinchannel(ctx, channel)


@bot.command()
async def setidle(ctx, seconds: int):
    global idle_timer
    idle_timer = seconds
    await ctx.send(f'The idle time was set to {seconds} seconds')


@bot.command()
async def lyrics(ctx):

    lyrics_display = musixmatch.track_lyrics_get(15953433)

    if lyrics_display is not None:
        await ctx.send(lyrics_display)


# Running the bot
bot.run(DISCORD_TOKEN)
