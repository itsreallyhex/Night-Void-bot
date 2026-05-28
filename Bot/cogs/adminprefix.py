import discord
from discord.ext import commands


class AdminPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def howmanyMemberCheck(self, ctx):
        await ctx.send(f"يوجد حالياً {len(ctx.guild.members)} عضو في نايت فويد")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def howmanyMemberCheckOnline(self, ctx):
        online_members = [member for member in ctx.guild.members
                          if (member.status != discord.Status.offline
                          or member.mobile_status != discord.Status.offline)
                          and not member.bot]
        await ctx.send(f"يوجد حالياً {len(online_members)} عضو متصل في نايت فويد")


async def setup(bot):
    await bot.add_cog(AdminPrefix(bot))