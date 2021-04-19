import discord
import youtube_dl
import asyncio
import urllib.request
import os
from secrets import MUSIXMATCH_TOKEN
from bs4 import BeautifulSoup
from discord.ext import commands
from musixmatch import Musixmatch
from pprint import pprint

musixmatch = Musixmatch(MUSIXMATCH_TOKEN)

global channel_default
channel_default = "general"
global created_channels
created_channels = []
global idle_timer
idle_timer = 300  # seconds (default 5 minutes)
global song_queue
song_queue = []
global display_lyrics
display_lyrics = True
global now_playing
now_playing = ""
global vote_skip
vote_skips = []


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="repeats current song", help="repeats the song that is currently playing"
    )
    async def repeat(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice.stop()
        voice.play(discord.FFmpegPCMAudio("song.mp3"))

    @commands.command(
        brief="skips to a specific time in the song",
        help="skips to a specific time in the song \n Usage: !seek 30",
    )
    async def seek(self, ctx, timestamp: int):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
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

    @commands.command(
        brief="plays a given song",
        help="plays the URL it is given \n Usage: !play https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )
    async def play(self, ctx, url: str):
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
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        print(voiceChannel)
        if voice is None:
            await voiceChannel.connect()
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

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
        while (
            voice.is_playing() or song_queue[0] is not url
        ):  # while song is playing or next song in queue is not url
            await asyncio.sleep(1)
        else:
            # updating the now_playing variable
            global now_playing
            now_playing = song_queue.pop(0)

        # downloading song into song.mp3
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                currentSong = file
                print(currentSong)
                os.rename(file, "song.mp3")

        voice.play(discord.FFmpegPCMAudio("song.mp3"))

        # finding lyrics and sent to test channel
        if display_lyrics is True:
            lyrics_channel = discord.utils.get(ctx.guild.text_channels, name="lyrics")
            guild = ctx.message.guild

            if lyrics_channel is None:
                await guild.create_text_channel("lyrics")
                lyrics_channel = discord.utils.get(
                    ctx.guild.text_channels, name="lyrics"
                )

            song_detail = currentSong.split("-")
            print(song_detail)

            song_artist = song_detail[0]
            song_title = song_detail[1]
            song_title = song_title.replace(".mp3", "")

            search_result = musixmatch.matcher_track_get(song_title, song_artist)
            pprint(search_result)

            song_artist = search_result["message"]["body"]["track"]["artist_name"]
            song_title = search_result["message"]["body"]["track"]["track_name"]
            song_id = search_result["message"]["body"]["track"]["track_id"]
            song_album = search_result["message"]["body"]["track"]["album_name"]
            song_url = search_result["message"]["body"]["track"]["track_share_url"]
            has_lyrics = search_result["message"]["body"]["track"]["has_subtitles"]

            if has_lyrics == 1:
                lyrics_display = musixmatch.track_lyrics_get(song_id)
                lyrics_to_send = lyrics_display["message"]["body"]["lyrics"][
                    "lyrics_body"
                ]
                await lyrics_channel.send(
                    f"```Now playing: {song_title}\nArtist: {song_artist}\nAlbum: {song_album}\n\n\n{lyrics_to_send}```"
                )
                embed = discord.Embed(title=f"{song_title}")
                embed.description = (
                    f"Like this song? Click [here]({song_url}) for full lyrics"
                )
                await lyrics_channel.send(embed=embed)
            else:
                await lyrics_channel.send(
                    f"There is no lyrics available for {song_title} :("
                )

        # idle check
        global idle_timer
        while (
            voice.is_playing() and len(voiceChannel.members) != 1
        ):  # checks if bot is playing music/if bot alone in voice
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

    @commands.command(
        brief="stops the song", help="stops the song that is currently playing"
    )
    async def stop(self, ctx):
        if song_queue:
            await ctx.send("Clearing queue...")
            song_queue.clear()
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice.stop()

    @commands.command(
        brief="skips the song", help="skips the song that is currently playing"
    )
    async def skip(self, ctx):
        # this is the old stop command, only stops current song and doesn't clear queue
        await ctx.send("Skipping song...")
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice.stop()

    @commands.command(
        brief="vote to skip the song",
        help="starts a vote to skip the song that is currently playing, requires majority vote"
    )
    async def voteskip(self, ctx):
        current_voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if ctx.message.author.voice.channel is None or ctx.message.author.voice.channel is not current_voice.channel:
            await ctx.send("You need to join the voice channel first!")
            return
        if len(song_queue) is 0:
            await ctx.send("Queue is empty, there is nothing to skip!")
            return

        member_count = len(current_voice.channel.members)
        required = int(member_count / 2)

        if ctx.message.author.id in vote_skips:
            await ctx.send("You already voted to skip!")
            return
        else:
            vote_skips.append(ctx.message.author.id)
            await ctx.send(f"You voted to skip the song! {len(vote_skips)}/{required} votes")

        if len(vote_skips) >= required:
            vote_skips.clear()
            await ctx.send("Skipping song...")
            current_voice.stop()


    @commands.command(brief="forces bot leave channel", help="forces bot leave channel")
    async def leave(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send("The bot is not in a channel.")

    @commands.command(
        brief="pauses the song",
        help="pauses the song that is currently playing, use !resume to continue",
    )
    async def pause(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("Nothing is playing.")

    @commands.command(
        brief="resumes playing song", help="plays the song that was last paused"
    )
    async def resume(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
        else:
            await ctx.send("Voice is not paused")

    @commands.command(
        brief="forces the bot to enter channel",
        help="forces the bot to enter channel \n if channel name is given but not created it will create the channel, if bot is playing in another channel it will resume in the specified channel\nUsage: !joinchannel General",
    )
    async def joinchannel(self, ctx, channel: str):
        voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=channel)
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
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

    @commands.command(
        brief="creates channel",
        help="creates a channel if the given channel does not already exist",
    )
    async def create(self, ctx, channel: str):
        guild = ctx.message.guild
        existing_channel = discord.utils.get(ctx.guild.channels, name=channel)

        if existing_channel is None:
            await guild.create_voice_channel(channel)
            await ctx.send("Channel created")
            global created_channels
            created_channels.append(discord.utils.get(ctx.guild.channels, name=channel))
        else:
            await ctx.send(f'Channel "{channel}" already exists')

    @commands.command(
        brief="removes given voice channel",
        help="removes given voice channel if it is empty, asks for verification \nUsage:!remove general",
    )
    async def remove(self, ctx, channel: str):
        channel = discord.utils.get(ctx.guild.channels, name=channel)
        channel_members = self.bot.get_channel(channel.id).members

        if channel is not None and not channel_members:
            await ctx.send(
                f'Are you sure you want to delete channel "{channel}"? (y or n)'
            )

            # below are requirements for user input, if not y or n will not accept the input
            def check(msg):
                return (
                    msg.author == ctx.author
                    and msg.channel == ctx.channel
                    and msg.content.lower() in ["y", "n"]
                )

            msg = await self.bot.wait_for(
                "message", check=check
            )  # waits for user input y or n
            if msg.content.lower() == "y":
                await channel.delete()
                await self.bot.setchannel(ctx, "general")
                print(channel_members)
                print(channel)
            else:
                await ctx.send("Cancelling...")
                print("Remove cancelled.")
        else:
            await ctx.send(
                f'Channel "{channel}" does not exist or has member(s) inside'
            )
            print(channel_members)
            print(channel)

    @commands.command(
        brief="sets the voice channel bot will be in",
        help="sets the bot to enter a specific channel \n \nUsage: !setchannel room1",
    )
    async def setchannel(self, ctx, channel: str):
        existing_channel = discord.utils.get(ctx.guild.channels, name=channel)
        guild = ctx.message.guild
        global channel_default

        if existing_channel is not None:
            channel_default = channel
            await ctx.send(f'set default playing channel to "{channel}"')
            print(channel_default)
            await self.bot.joinchannel(ctx, channel)
        else:
            channel_default = channel
            await guild.create_voice_channel(channel)
            await ctx.send("Channel created and set to default playing channel")
            await self.bot.joinchannel(ctx, channel)

    @commands.command(
        brief="sets the idle time for the bot to leave",
        help="how to set the amount of time the bot will sit inactive until leaving\n usage:!setidle 20",
    )
    async def setidle(self, ctx, seconds: int):
        global idle_timer
        idle_timer = seconds
        await ctx.send(f"The idle time was set to {seconds} seconds")

    @commands.command(
        brief="displays the song queue",
        help="displays a list of all the currently queued songs",
    )
    async def queue(self, ctx):
        if len(song_queue) is 0:
            await ctx.send("Queue is empty! Try using the !play command.")
        else:
            embed = discord.Embed(title="Song Queue:")
            for song in song_queue:
                index = song_queue.index(song) + 1
                soup = BeautifulSoup(urllib.request.urlopen(song), "html.parser")
                song_title = str(soup.title)
                song_title = song_title.replace("<title>", "")
                song_title = song_title.replace("</title>", "")
                embed.add_field(name=f"Song #{index}:", value=f"{song_title}", inline=True)
            await ctx.send(embed=embed)

    @commands.command(
        brief="displays song lyrics",
        help="displays the song lyrics that is currently playing "
        "in the #lyrics channel",
    )
    async def lyrics(self, ctx, command: str):
        global display_lyrics
        existing_channel = discord.utils.get(ctx.guild.channels, name="lyrics")
        if command == "on":
            display_lyrics = True
            await ctx.send("Displaying Lyrics : ON")
        elif command == "off":
            display_lyrics = False
            await existing_channel.delete()
            await ctx.send("Displaying Lyrics : OFF")
        else:
            await ctx.send("I cannot understand your command :(")

    @commands.command()
    async def searchlyrics(ctx, song_title: str, song_artist=None):
        search_channel = discord.utils.get(ctx.guild.channels, name="search-result")
        guild = ctx.message.guild

        if song_title == "clear" and song_artist is None:
            await search_channel.delete()
        else:
            # create test channel if does not exist
            if search_channel is None:
                await guild.create_text_channel("search result")
                search_channel = discord.utils.get(
                    ctx.guild.text_channels, name="search-result"
                )
            # search for lyrics
            search_result = musixmatch.matcher_track_get(song_title, song_artist)
            status_code = search_result["message"]["header"]["status_code"]

            if status_code == 404:
                await ctx.send("Cannot find lyrics for this song :(")
            else:
                song_artist = search_result["message"]["body"]["track"]["artist_name"]
                song_title = search_result["message"]["body"]["track"]["track_name"]
                song_id = search_result["message"]["body"]["track"]["track_id"]
                song_album = search_result["message"]["body"]["track"]["album_name"]
                song_url = search_result["message"]["body"]["track"]["track_share_url"]
                has_lyrics = search_result["message"]["body"]["track"]["has_subtitles"]

                # check if has lyrics
                if has_lyrics == 1:
                    lyrics_search = musixmatch.track_lyrics_get(song_id)
                    lyrics_send = lyrics_search["message"]["body"]["lyrics"][
                        "lyrics_body"
                    ]
                    embed = discord.Embed(
                        title="Search Result:",
                        description=f"Song Title: {song_title}\nArtist: {song_artist}\nAlbum: {song_album}",
                        color=0xFF3838,
                    )
                    embed.add_field(
                        name="Lyrics:",
                        value=f"{lyrics_send}\n\nClick [here]({song_url}) for full lyrics",
                    )
                    await ctx.send("Lyrics found! Please check search result")
                    await search_channel.send(embed=embed)
                else:
                    await ctx.send("There is no lyrics available for this song :( :(")

    @commands.command(
            brief="displays currently playing song",
            help="displays the title of the song currently playing",
        )
    async def nowplaying(self, ctx):
        global now_playing
        soup = BeautifulSoup(urllib.request.urlopen(now_playing), "html.parser")
        song_title = str(soup.title)
        song_title = song_title.replace("<title>", "")
        song_title = song_title.replace("</title>", "")
        if discord.utils.get(self.bot.voice_clients, guild=ctx.guild) is None:
            await ctx.send("Bot is not currently in a voice channel! Try using the !play command.")
        else:
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing() or voice.is_paused():
            embed = discord.Embed(title="Now Playing:", description=f"{song_title}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("No song is currently being played! Try using the !play command.")

def setup(bot):
    bot.add_cog(Music(bot))
