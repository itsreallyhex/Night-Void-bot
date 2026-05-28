import discord
from discord.ext import commands
from discord import app_commands


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
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="يعطيك صورة البروفايل حقك")
    async def avatar(self, interaction: discord.Interaction):
        member = interaction.user
        embed = discord.Embed(
            title=f"صورة البروفايل حق {member}",
            color=0x3498DB
        )
        embed.set_image(url=member.avatar.url)
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="servericon", description="يعطيك صورة الايكون حق السيرفر")
    async def servericon(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"صورة الايكون حق {interaction.guild.name}",
            color=0xE67E22
        )
        embed.set_image(url=interaction.guild.icon.url)
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)
    


async def setup(bot):
    await bot.add_cog(MemberSlash(bot))