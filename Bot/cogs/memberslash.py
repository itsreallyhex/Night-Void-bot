import discord
from discord.ext import commands
from discord import app_commands
import discord.ui
from utilities import BotMentions, EphemeralReply
from logger import setup_logger
logger = setup_logger("NightVoid.MemberSlashCog")


class MemberSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="يعطيك معلومات عن السيرفر")
    async def serverinfo(self, interaction: discord.Interaction):
        human_count = len([m for m in interaction.guild.members if not m.bot])
        embed = discord.Embed(
            title=f"معلومات عن {interaction.guild.name}",
            description=(
                f"عدد الأعضاء: **{human_count}**\n"
                f"عدد الرولات: **{len(interaction.guild.roles)}**\n"
                f"صاحب السيرفر: **{interaction.guild.owner}**"
            ),
            color=0xE67E22
        )
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="يعطيك معلومات عن نفسك")
    async def userinfo(self, interaction: discord.Interaction):
        member = interaction.user
        embed = discord.Embed(
            title=f"معلومات عن {member}",
            description=(
                f"الاسم الكامل: **{member}**\n"
                f"تاريخ الانضمام: **{member.joined_at.strftime('%Y-%m-%d')}**\n"
                f"الحالة: **{member.status}**"
            ),
            color=0x9B59B6
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="يعطيك صورة البروفايل حق اي شخص تحدده")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member):
        embed = discord.Embed(
            title=f"صورة البروفايل حق {member}",
            color=0x3498DB
        )
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="servericon", description="يعطيك صورة الايكون حق السيرفر")
    async def servericon(self, interaction: discord.Interaction):
        if not interaction.guild.icon:
            await interaction.response.send_message("❌ ما عند السيرفر صورة ايكون.", ephemeral=True)
            return
        embed = discord.Embed(
            title=f"صورة الايكون حق {interaction.guild.name}",
            color=0xE67E22
        )
        embed.set_image(url=interaction.guild.icon.url)
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="makeembed", description="يساعدك تصنع امبد خاص فيك")
    async def makeembed(self, interaction: discord.Interaction, title: str, text: str):
        embed = discord.Embed(
            title=title,
            description=text,
            color=discord.Color.random()
        )
        embed.set_footer(text=f"تم صناع الامبد من قبل {interaction.user}")
        await interaction.response.send_message(embed=embed)

    #@app_commands.command(name="randomnumber", description="يعطيك رقم عشوائي بين رقمين تحددهم")
    #async def randomnumber(self, interaction: discord.Interaction, min: int, max: int):
        #if min > max:
          #  await interaction.response.send_message("الرقم الأول لازم يكون أصغر من الرقم الثاني.")
           # return
        #number = random.randint(min, max)
        #await interaction.response.send_message(f"الرقم العشوائي بين {min} و {max} هو: **{number}**")
    @app_commands.command(name="social", description="يعطيك روابط السوشيال ميديا حق hex, فايز")
    async def social(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="روابط السوشيال ميديا حق Hex",
            description=(
                f"{BotMentions.Hex()}🔹 **Hex **\n"
                "   - [يوتيوب](https://www.youtube.com/@itsreallyhex)\n"
                "   - [انستجرام](https://www.instagram.com/igitshex/)\n"
               # "   - [تيك توك](https://www.tiktok.com/)\n\n"
               # f"{BotMentions.fayz()}🔹 **فايز**\n"
               # "   - [يوتيوب](https://www.youtube.com/@FayzVoid)\n"
               # "   - [انستجرام](https://www.instagram.com/fayzvoid/)\n"
               # "   - [تيك توك](https://www.tiktok.com/@fayzvoid)"
            ),
            color=0x1ABC9C
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="botinfo", description="يعطيك معلومات عن البوت")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="معلومات عن البوت",
            description=(
                f"الاسم: **{self.bot.user}**\n"
                f"المطور: {BotMentions.Hex()}\n"
                f"تاريخ الإنشاء: **{self.bot.user.created_at.strftime('%Y-%m-%d')}**\n"
                f"عدد الأعضاء: **{len(self.bot.users)}**"
            ),
            color=0x3498DB
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MemberSlash(bot))