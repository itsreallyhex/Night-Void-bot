import discord
from discord.ext import commands


class MemberPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nightvoid(self, ctx):
        embed = discord.Embed(
            title="نايت فويد 🌙",
            description="بوت تم تطويره بواسطة <@904399821580943420>و<@1005827322844282951>. يهدف إلى تقديم تجربة فريدة وممتعة للأعضاء.",
            color=0x9B59B6
        )
        embed.add_field(name="الوظائف", value="إدارة الأدوار، التفاعل مع الأعضاء، معلومات الخادمب واكثر قادم.", inline=False)
        embed.add_field(name="واجاهت مشكلة اثناء استخدام البوت؟", value="تواصل مع الإدارة", inline=False)
        embed.set_footer(text="نايت فويد | Night Void")
        await ctx.send(embed=embed)

    @commands.command()
    async def prefix(self, ctx):
        embed = discord.Embed(
            title="البريفكس",
            description="البوت يستخدم البريفكس التالي: `!`",
            color=0x3498DB
        )
        embed.add_field(name="معلومات من البوت", value="!nightvoid", inline=True)
        embed.set_footer(text="نايت فويد | Night Void")
        await ctx.send(embed=embed)
    


async def setup(bot):
    await bot.add_cog(MemberPrefix(bot))