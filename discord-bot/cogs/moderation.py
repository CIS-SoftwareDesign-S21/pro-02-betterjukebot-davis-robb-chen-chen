import discord
from discord.ext import commands
from secrets import GIPHY_TOKEN


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention}')

    @commands.command()
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if(user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return

    @commands.command()
    async def addrole(self, ctx, role: discord.Role, user: discord.Member):
        if ctx.author.guild_permissions.administrator:
            await user.add_roles(role)
            await ctx.send(f'Successfully given {role.mention} to {user.mention}.')

    @commands.command()
    async def removerole(self, ctx, role: discord.Role, user: discord.Member):
        if ctx.author.guild_permissions.administrator:
            await user.remove_roles(role)
            await ctx.send(f'Successfully removed {role.mention} to {user.mention}.')


def setup(bot):
    bot.add_cog(Moderation(bot))
