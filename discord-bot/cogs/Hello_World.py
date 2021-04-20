import discord
from discord.ext import commands


class Hello_World(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="prints 'hello_world'", help="prints 'hello_world' our minimal project"
    )
    async def hw(self, ctx):
        await ctx.send("Hello World!")

    @commands.command(brief="prints 'soup!'", help="prints 'soup!' as a Ju-Hung test ")
    async def soup(self, ctx):
        await ctx.send("Soup!")

    @commands.command(brief="prints 'Becca'", help="prints 'Becca' as a Becca test")
    async def goober(self, ctx):
        await ctx.send("Becca")

    @commands.command(
        brief="prints ':angry:'", help="angry emoji command prints ':angry:'"
    )
    async def angry(self, ctx):
        await ctx.send(":angry:")

    @commands.command(
        brief="prints ':angry::rage: array'",
        help="angryarray emoji command prints ':angry::rage: array'",
    )
    async def angryarray(self, ctx):
        await ctx.send(
            ":angry::rage::angry:\n:rage::angry::rage:" "\n:angry::rage::angry:"
        )


def setup(bot):
    bot.add_cog(Hello_World(bot))
