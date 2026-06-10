import discord
import platform
import psutil
import os
from discord.ext import commands
from discord import app_commands
from utilities import PermissionChecker
from logger import setup_logger

_logger = setup_logger("NightVoid.OwnerCommands")

# THIS COMMAND/PREFIX ONLY FOR OWNER OF THE BOT. NOT SERVER OWNER.
class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return
        synced = await self.bot.tree.sync()
        await ctx.send(f"✅ تم مزامنة {len(synced)} أمر")

    @commands.command()
    async def reload(self, ctx):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return

        failed = []
        success = 0

        for extension in list(self.bot.extensions.keys()):
            try:
                await self.bot.reload_extension(extension)
                _logger.info(f"Reloaded: {extension}")
                success += 1
            except Exception as e:
                _logger.error(f"Failed to reload {extension}: {e}")
                failed.append(extension)

        if failed:
            await ctx.send(f"✅ تم إعادة تحميل {success} | ❌ فشل: {', '.join(failed)}")
        else:
            await ctx.send(f"✅ تم إعادة تحميل {success} cogs بنجاح")

    # Claude helped me to make this btw
    @commands.command()
    async def botstats(self, ctx):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return

        process = psutil.Process(os.getpid())
        memory = process.memory_info().rss / 1024 / 1024
        uptime = discord.utils.utcnow() - self.bot.start_time

        embed = discord.Embed(title="🤖 Bot Stats", color=0x2b2d31)
        embed.add_field(name="السيرفرات", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="المستخدمين", value=len(self.bot.users), inline=True)
        embed.add_field(name="Memory", value=f"{memory:.2f} MB", inline=True)
        embed.add_field(name="Uptime", value=str(uptime).split(".")[0], inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))