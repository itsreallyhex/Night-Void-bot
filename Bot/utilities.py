import discord
from discord.ext import commands
from discord import app_commands
from logger import setup_logger

_logger = setup_logger("NightVoid.Utilities")

COOLDOWN_SECONDS = 20

def slash_cooldown(seconds: int = COOLDOWN_SECONDS):
    """Per-user cooldown decorator for slash (app) commands."""
    return app_commands.checks.cooldown(1, seconds, key=lambda i: i.user.id)

def prefix_cooldown(seconds: int = COOLDOWN_SECONDS):
    """Per-user cooldown decorator for prefix commands."""
    return commands.cooldown(1, seconds, commands.BucketType.user)


class AdminSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        _logger.info("AdminSlash cog loaded")


class MemberSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        _logger.info("MemberSlash cog loaded")


class AdminPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        _logger.info("AdminPrefix cog loaded")


class MemberPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        _logger.info("MemberPrefix cog loaded")

class PermissionChecker:
    @staticmethod
    def is_admin(member: discord.Member) -> bool:
        return member.guild_permissions.administrator

    @staticmethod
    def has_permission(member: discord.Member, permission: str) -> bool:
        return getattr(member.guild_permissions, permission, False)

    # Check if the user is the guild owner/ Server owner
    @staticmethod
    def is_guild_owner(member: discord.Member) -> bool:
        return member.guild.owner_id == member.id

    # Check if the user is the bot owner. Aka the person who created the bot 
    @staticmethod
    async def is_bot_owner(bot: commands.Bot, user: discord.User) -> bool:
        return await bot.is_owner(user)
class EphemeralReply:
    @staticmethod
    async def send(interaction, message: str):
        await interaction.response.send_message(message, ephemeral=True)

    @staticmethod
    async def send_embed(interaction, embed):
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Utility class for bot mentions
class BotMentions:
    @staticmethod
    def Hex():
        return "<@904399821580943420>"

    @staticmethod
    def fayz():
        return "<@1005827322844282951>"
    
    @staticmethod
    def everyone():
        return "@everyone"
    
    @staticmethod
    def user(user: discord.User):
        return f"<@{user.id}>"