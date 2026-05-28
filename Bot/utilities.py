from discord.ext import commands


class AdminSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("AdminSlash cog loaded")


class MemberSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("MemberSlash cog loaded")


class AdminPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("AdminPrefix cog loaded")


class MemberPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("MemberPrefix cog loaded")

class PermissionChecker:
    @staticmethod
    def is_admin(member) -> bool:
        return member.guild_permissions.administrator

    @staticmethod
    def has_permission(member, permission: str) -> bool:
        return getattr(member.guild_permissions, permission, False)
