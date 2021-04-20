import discord
from discord.ext import commands
from secrets import GIPHY_TOKEN


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="Kicks mentioned user",
        help="Kicks mentioned user \nUsage: !kick '@User'",
    )
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)

    @commands.command(
        brief="Bans mentioned user",
        help="Bans mentioned user \nUsage: !ban '@User'",
    )
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member.mention}")

    @commands.command(
        brief="Unbans mentioned user",
        help="Unbans mentioned user \nUsage: !unban '@User'",
    )
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"fUnbanned {user.mention}")
                return

    @commands.command(
        brief="Adds existing role to user",
        help="Adds existing role to user, requires administrator permissions \nUsage: !addrole 'Role' '@User'",
    )
    async def addrole(self, ctx, role: discord.Role, user: discord.Member):
        if ctx.author.guild_permissions.administrator:
            await user.add_roles(role)
            await ctx.send(f"Successfully given {role.mention} to {user.mention}.")
        else:
            await ctx.send("You don't have permission goober")

    @commands.command(
        brief="Removes role from user",
        help="Removes role from user, requires administrator permissions \nUsage: !removerole 'Role' '@User'",
    )
    async def removerole(self, ctx, role: discord.Role, user: discord.Member):
        if ctx.author.guild_permissions.administrator:
            await user.remove_roles(role)
            await ctx.send(f"Successfully removed {role.mention} from {user.mention}.")
        else:
            await ctx.send("You don't have permission goober")

    @commands.command(
        brief="Counts how many messages users have made in the discord",
        help="Counts how many messages users have made in the discord \nProviding channel is optional \nUsage: !participation *'Channel'",
    )
    async def participation(self, ctx, channel=None):
        channel_list = []
        counter = 0
        current_guild = ctx.message.guild.id
        members = ctx.message.guild.members
        members.remove(self.bot.user)
        # print(current_guild)
        # print(members)
        for guild in self.bot.guilds:
            if guild.id == current_guild:
                for text_channel in guild.text_channels:
                    channel_list.append(text_channel)

        # print(channel_list)

        if channel != None:
            if guild.id == current_guild:
                for text_channel in guild.text_channels:
                    if text_channel.name == channel:
                        channel_list.clear()
                        channel_list.append(text_channel)
                        break

        if len(channel_list) > 1 and channel != 1:
            await ctx.send(f"Channel {channel} does not exist")
            return None

        print(channel_list)

        for member in members:
            for channel in channel_list:
                async for message in channel.history(limit=None):
                    if message.author.id == member.id:
                        counter += 1
                print(str(channel) + str(counter))
            await ctx.send(f"{member} has made {counter} messages")
            counter = 0


def setup(bot):
    bot.add_cog(Moderation(bot))