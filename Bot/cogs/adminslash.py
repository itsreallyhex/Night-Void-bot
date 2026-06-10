import discord
from discord.ext import commands
from discord import app_commands
from utilities import PermissionChecker, EphemeralReply
from logger import setup_logger
logger = setup_logger("NightVoid.AdminSlashCog")

class AdminSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="تحقق من تأخير البوت (ادمن فقط)")
    async def ping(self, interaction: discord.Interaction):
        if not PermissionChecker.is_admin(interaction.user):
            await EphemeralReply.send(interaction, "❌ ما عندك صلاحية!")
            return
        embed = discord.Embed(
            title="بونج",
            description=f"تأخير البوت: **{round(self.bot.latency * 1000)}ms**",
            color=0x2ECC71
        )
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="showmemberinfo", description="يعطيك معلومات عن العضو (ادمن فقط)")
    async def show_member_info(self, interaction: discord.Interaction, member: discord.Member):
        if not PermissionChecker.is_admin(interaction.user):
            await EphemeralReply.send(interaction, "❌ ما عندك صلاحية!")
            return
        embed = discord.Embed(
            title=f"معلومات عن {member}",
            description=(
                f"الاسم الكامل: **{member}**\n"
                f"الرتب: **{', '.join([role.name for role in member.roles if role.name != '@everyone'])}**\n"
                f"تاريخ الانضمام: **{member.joined_at.strftime('%Y-%m-%d')}**\n"
                f"الحالة: **{member.status}**"
            ),
            color=0xE74C3C
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="showroleinfo", description="يعطيك معلومات عن الرتبة (ادمن فقط)")
    async def show_role_info(self, interaction: discord.Interaction, role: discord.Role):
        if not PermissionChecker.is_admin(interaction.user):
            await EphemeralReply.send(interaction, "❌ ما عندك صلاحية!")
            return
        embed = discord.Embed(
            title=f"معلومات عن الرتبة {role.name}",
            description=(
                f"عدد الأعضاء: **{len(role.members)}**\n"
                f"اللون: **{role.color}**\n"
                f"الترتيب: **{role.position}**"
            ),
            color=role.color
        )
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="getchannelinfo", description="يعطيك معلومات عن الروم (ادمن فقط)")
    async def get_channel_info(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not PermissionChecker.is_admin(interaction.user):
            await EphemeralReply.send(interaction, "❌ ما عندك صلاحية!")
            return
        messages = [msg async for msg in channel.history(limit=None)]
        embed = discord.Embed(
            title=f"معلومات عن الروم {channel.name}",
            description=(
                f"نوع الروم: **{str(channel.type).split('.')[-1]}**\n"
                f"عدد الرسائل: **{len(messages)}**\n"
                f"تاريخ الإنشاء: **{channel.created_at.strftime('%Y-%m-%d')}**"
            ),
            color=0x8E44AD
        )
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warning", description="يعطيك تحذير (ادمن فقط)")
    async def warning(self, interaction: discord.Interaction, user: discord.User, reason: str):
        if not PermissionChecker.is_admin(interaction.user):
            await EphemeralReply.send(interaction, "❌ ما عندك صلاحية!")
            return
        try:
            await user.send(f"⚠️ تم إصدار تحذير لك في **{interaction.guild.name}**: {reason}")
            await EphemeralReply.send(interaction, f"✅ تم إرسال التحذير لـ {user.mention} في الخاص.")
        except discord.Forbidden:
            await EphemeralReply.send(interaction, f"❌ تعذّر إرسال الخاص لـ {user.mention}، ربما أغلق الرسائل الخاصة.")

    @app_commands.command(name="listbannedusers", description="يعطيك قائمة بالأعضاء المحظورين (ادمن فقط)")
    async def list_banned_users(self, interaction: discord.Interaction):
        if not PermissionChecker.is_admin(interaction.user):
            await EphemeralReply.send(interaction, "❌ ما عندك صلاحية!")
            return
        banned_users = await interaction.guild.bans()
        if not banned_users:
            await interaction.response.send_message("لا يوجد أعضاء محظورين في هذا السيرفر.")
            return
        embed = discord.Embed(
            title="قائمة الأعضاء المحظورين",
            description="\n".join([f"**{ban_entry.user}** - {ban_entry.reason or 'بدون سبب'}" for ban_entry in banned_users]),
            color=0xC0392B
        )
        embed.set_footer(text="نايت فويد | Night Void")
        await interaction.response.send_message(embed=embed)
    


async def setup(bot):
    await bot.add_cog(AdminSlash(bot))
