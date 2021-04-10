import discord
from discord.ext.commands import Bot
import os
import asyncio
import youtube_dl
import random
import giphy_client
import urllib.request

# import musixmatch
from giphy_client.rest import ApiException
from pprint import pprint
from secrets import DISCORD_TOKEN, GIPHY_TOKEN
from pyrandmeme import *
from bs4 import BeautifulSoup


# Creating the Bot
bot = Bot(command_prefix="!")
global channel_default
channel_default = "general"
global created_channels
created_channels = []
global idle_timer
idle_timer = 300  # seconds (default 5 minutes)
global song_queue
song_queue = []


@bot.event
async def on_ready():
    print("Connected to bot: {}".format(bot.user.name))
    print("Bot ID: {}".format(bot.user.id))


@bot.listen("on_message")
async def trigger_words(message):
    # Whenever a user other than bot says "hi"
    if message.content == "hi":
        await message.channel.send("Hi there!!! " + message.author.mention)
        await message.channel.send(await search_gifs("hi"))

    elif message.content == "hello":
        await message.channel.send("Hello :) " + message.author.mention)
        await message.channel.send(await search_gifs("hello"))

    elif message.content == "welcome":
        await message.channel.send(
            message.author.mention + " Welcome to the discord channel :)")
        await message.channel.send(await search_gifs("welcome"))

    elif message.content == "bye":
        await message.channel.send(
            message.author.mention + " May the force be with you")
        await message.channel.send(await search_gifs("star wars bye"))

    elif message.content == "good bye":
        await message.channel.send(message.author.mention + " Live long and prosper")
        await message.channel.send(await search_gifs("salute"))

    elif message.content == "goober":
        await message.channel.send(message.author.mention + " You're a goober! www")
        await message.channel.send(await search_gifs("goober"))

    elif message.content == "lol":
        await message.channel.send(message.author.mention + " www")
        await message.channel.send(await search_gifs("www"))

    elif message.content == "www":
        await message.channel.send(message.author.mention + " www")
        await message.channel.send(await search_gifs("laughing"))


#########################################################
# Create an instance of the API class
api_instance = giphy_client.DefaultApi()
config = {
    "api_key": GIPHY_TOKEN,
    "limit": 1,
    "rating": "g",
}  # Giphy API Key,
try:
    api_response = api_instance.gifs_trending_get(
        config["api_key"], limit=config["limit"], rating=config["rating"]
    )
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->gifs_trending_get: %s\n" % e)
#########################################################


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
        await ctx.send("Song added to queue.")
        global song_queue
        song_queue.append(url)
        return

    # defining voice channel and joining if not already connected
    print(channel_default)
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=channel_default)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    print(voiceChannel)
    if voice is None:
        await voiceChannel.connect()
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # YouTube api stuff
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

    # adding to queue and awaiting next song to be played
    song_queue.append(url)
    if voice.is_playing():
        await ctx.send("Song added to queue.")
    while voice.is_playing() or song_queue[0] is not url: # while song is playing or next song in queue is not url
        await asyncio.sleep(1)
    else:
        song_queue.pop(0)

    # downloading song into song.mp3
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")
    voice.play(discord.FFmpegPCMAudio("song.mp3"))

    # idle check ***could possible be moved into a @tasks or a listener method***
    global idle_timer
    while voice.is_playing() and len(voiceChannel.members) != 1:  # checks if bot is playing music/if bot alone in voice
        await asyncio.sleep(1)
    else:
        if len(voiceChannel.members) != 1:
            url = song_queue.pop(0)
            await play(ctx, url)
            return
        await asyncio.sleep(idle_timer)
        while voice.is_playing() and len(voiceChannel.members) != 1:
            break
        else:
            await voice.disconnect()
            for created in created_channels:
                if voiceChannel == created:
                    await voiceChannel.delete()


@bot.command()
async def stop(ctx):
    if song_queue:
        await ctx.send("Clearing queue...")
        song_queue.clear()
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()

@bot.command()
async def skip(ctx): # this is the old stop command, only stops current song and doesn't clear queue
    await ctx.send("Skipping song...")
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
            return (
                msg.author == ctx.author
                and msg.channel == ctx.channel
                and msg.content.lower() in ["y", "n"]
            )

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
    await ctx.send(f"The idle time was set to {seconds} seconds")


@bot.command()
async def queue(ctx):
    global song_queue
    await ctx.send("Song Queue:")
    for song in song_queue:
        index = song_queue.index(song) + 1
        soup = BeautifulSoup(urllib.request.urlopen(song), "html.parser")
        song_title = soup.title
        song_title.replace("<title>", "")
        song_title.replace("</title>", "")
        await ctx.send(f"#{index}: {song_title}")


# # was working, then stopped. May need a new library or implement manual solution
# @bot.command()
# async def meme(ctx):
#     await ctx.send(embed=await pyrandmeme())


@bot.command()
async def lobsters(ctx):
    await ctx.send(file=discord.File("lobsters.gif"))


@bot.command(name="8ball")
async def magic_eight_ball(ctx):
    response = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes – definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful.",
    ]
    answer = random.choice(response)
    await ctx.send(answer)
    gif = await search_gifs(answer)
    await ctx.send("Gif URL : " + gif)


async def search_gifs(query):
    try:
        response = api_instance.gifs_search_get(GIPHY_TOKEN, query, limit=5, rating="g")
        lst = list(response.data)
        gif = random.choices(lst)

        return gif[0].url

    except ApiException as e:
        return "Exception when calling DefaultApi->gifs_search_get: %s\n" % e


# Running the bot
bot.run(DISCORD_TOKEN)
