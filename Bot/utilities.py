import discord
from discord.ext import commands
from logger import setup_logger
_logger = setup_logger("NightVoid.Utilities")


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
    def is_admin(member) -> bool:
        return member.guild_permissions.administrator

    @staticmethod
    def has_permission(member, permission: str) -> bool:
        return getattr(member.guild_permissions, permission, False)
    
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