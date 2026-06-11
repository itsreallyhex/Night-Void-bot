import discord
import platform
import psutil
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from utilities import PermissionChecker, prefix_cooldown
from logger import setup_logger

_logger = setup_logger("NightVoid.OwnerCommands")

# THIS COMMAND/PREFIX ONLY FOR OWNER OF THE BOT. NOT SERVER OWNER.
class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @prefix_cooldown()
    async def sync(self, ctx):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return
        self.bot.tree.clear_commands(guild=None)
        await self.bot.tree.sync()  
        self.bot.tree.copy_global_to(guild=self.bot.main_guild)
        synced = await self.bot.tree.sync(guild=self.bot.main_guild)
        await ctx.send(f"✅ تم مزامنة {len(synced)} أمر (سيرفر)")

    @commands.command()
    @prefix_cooldown()
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

    # All codes under this was made by the helpe of Claude Code.
    @commands.command()
    @prefix_cooldown()
    async def botstats(self, ctx):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return

        process = psutil.Process(os.getpid())
        memory = process.memory_info().rss / 1024 / 1024
        uptime = discord.utils.utcnow() - self.bot.start_time

        embed = discord.Embed(title="معلومات البوت", color=0x2b2d31)
        embed.add_field(name="السيرفرات", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="الذاكرة", value=f"{memory:.2f} MB", inline=True)
        embed.add_field(name="وقت التشغيل", value=str(uptime).split(".")[0], inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)

        await ctx.send(embed=embed)

    # Usage: !setstatus playing Valorant | !setstatus watching the server | !setstatus clear
    @commands.command()
    @prefix_cooldown()
    async def setstatus(self, ctx, activity_type: str = None, *, text: str = None):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return

        if activity_type == "clear":
            await self.bot.change_presence(activity=None)
            await ctx.send("✅ تم مسح الحالة")
            return

        types = {
            "playing": discord.ActivityType.playing,
            "watching": discord.ActivityType.watching,
            "listening": discord.ActivityType.listening,
            "competing": discord.ActivityType.competing,
        }

        if activity_type not in types or text is None:
            await ctx.send("❌ الاستخدام: `!setstatus <playing|watching|listening|competing> <نص>` أو `!setstatus clear`")
            return

        activity = discord.Activity(type=types[activity_type], name=text)
        await self.bot.change_presence(activity=activity)
        _logger.info(f"Status changed to: {activity_type} {text}")
        await ctx.send(f"✅ تم تغيير الحالة إلى: **{activity_type} {text}**")

    # Usage: !dmall <message> — DMs every (non-bot) member with a delay to avoid spam flags
    @commands.command()
    @prefix_cooldown()
    async def dmall(self, ctx, *, message: str = None):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return

        if message is None:
            await ctx.send("❌ الاستخدام: `!dmall <نص الرسالة>`")
            return

        members = [m for m in ctx.guild.members if not m.bot]

        # Confirmation step — this messages a lot of people, so make it deliberate.
        await ctx.send(
            f"⚠️ راح ترسل رسالة خاصة إلى **{len(members)}** عضو. "
            f"رد بـ `yes` خلال 30 ثانية للتأكيد."
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "yes"

        try:
            await self.bot.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send("❌ تم الإلغاء (انتهى الوقت)")
            return

        sent = 0
        failed = 0
        status = await ctx.send(f"📨 جاري الإرسال... 0/{len(members)}")

        for i, member in enumerate(members, 1):
            try:
                await member.send(message)
                sent += 1
            except discord.Forbidden:
                # Member has DMs closed or blocked the bot.
                failed += 1
            except discord.HTTPException as e:
                failed += 1
                _logger.error(f"Failed to DM {member.id}: {e}")

            if i % 10 == 0:
                await status.edit(content=f"📨 جاري الإرسال... {i}/{len(members)}")

            await asyncio.sleep(1.5)

        _logger.info(f"dmall by {ctx.author.id}: sent={sent} failed={failed}")
        await status.edit(content=f"✅ تم الإرسال: **{sent}** | ❌ فشل: **{failed}**")


async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))