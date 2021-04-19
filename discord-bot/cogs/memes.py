import discord
import giphy_client
import random
from discord.ext import commands
from secrets import GIPHY_TOKEN
from giphy_client.rest import ApiException
from pprint import pprint
from pyrandmeme import *

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


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def trigger_words(self, message):
        # Whenever a user other than bot says "hi"
        if message.content == "hi":
            await message.channel.send("Hi there!!! " + message.author.mention)
            await message.channel.send(await search_gifs("hi"))

        elif message.content == "hello":
            await message.channel.send("Hello :) " + message.author.mention)
            await message.channel.send(await search_gifs("hello"))

        elif message.content == "welcome":
            await message.channel.send(
                message.author.mention + " Welcome to the discord channel :)"
            )
            await message.channel.send(await search_gifs("welcome"))

        elif message.content == "bye":
            await message.channel.send(
                message.author.mention + " May the force be with you"
            )
            await message.channel.send(await search_gifs("star wars bye"))

        elif message.content == "good bye":
            await message.channel.send(
                message.author.mention + " Live long and prosper"
            )
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

    @commands.command(
        brief="sends a random meme", help="sends a random meme \nUsage: !meme"
    )
    async def meme(self, ctx):
        await ctx.send(embed=await pyrandmeme())

    @commands.command(brief="sends a special gif", help="BRING IN THE DANCING LOBSTERS")
    async def lobsters(self, ctx):
        await ctx.send(file=discord.File("lobsters.gif"))

    @commands.command(
        name="8ball", brief="ask a question and it will answer", help="\nUsage: !8ball"
    )
    async def magic_eight_ball(self, ctx):
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


def setup(bot):
    bot.add_cog(Memes(bot))
