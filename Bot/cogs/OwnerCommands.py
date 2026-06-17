import discord
import platform
import psutil
import os
import asyncio
from typing import Optional
from discord.ext import commands, tasks
from discord import app_commands
from utilities import PermissionChecker, prefix_cooldown
from logger import setup_logger

_logger = setup_logger("NightVoid.OwnerCommands")

ACTIVITY_TYPES = {
    "playing": discord.ActivityType.playing,
    "watching": discord.ActivityType.watching,
    "listening": discord.ActivityType.listening,
    "competing": discord.ActivityType.competing,
}


def _format_elapsed(delta) -> str:
    """Turn a timedelta into a short '2d 3h 15m' string for the status."""
    total_minutes = int(delta.total_seconds() // 60)
    days, rem = divmod(total_minutes, 1440)
    hours, minutes = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


# THIS COMMAND/PREFIX ONLY FOR OWNER OF THE BOT. NOT SERVER OWNER.
class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


        # The custom-status feature is fully optional: if STATUS_TEXT isn't set in
        # the environment, status_text stays None and the bot just runs without it.
        self.status_type = os.getenv("STATUS_TYPE", "watching")
        self.status_text = os.getenv("STATUS_TEXT") or None
        self.status_since = discord.utils.utcnow()
        self._status_updater.start()

    def cog_unload(self):
        # Stop the loop when the cog is reloaded/unloaded so we don't stack timers.
        self._status_updater.cancel()

    def _build_activity(self) -> discord.BaseActivity:
        """Build the presence from the current status state (+ timer for verb types)."""
        if self.status_type == "custom":  # note-style: verb-less, no timer, just the text
            return discord.CustomActivity(name=self.status_text)
        elapsed = _format_elapsed(discord.utils.utcnow() - self.status_since)
        atype = ACTIVITY_TYPES.get(self.status_type, discord.ActivityType.watching)
        return discord.Activity(type=atype, name=f"{self.status_text} • {elapsed}")

    # Refreshes the presence once a minute so the "watching for X" timer ticks.
    # Discord rate-limits presence updates, so a 1-minute cadence is the safe choice.
    @tasks.loop(minutes=1)
    async def _status_updater(self):
        if not self.status_text:  # None == not configured or cleared
            return
        await self.bot.change_presence(activity=self._build_activity())

    @_status_updater.before_loop
    async def _before_status_updater(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @prefix_cooldown()
    async def sync(self, ctx):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return
        guild = self.bot.main_guild
        # 1. Copy the (still-in-memory) global commands into the guild and register them.
        self.bot.tree.copy_global_to(guild=guild)
        synced = await self.bot.tree.sync(guild=guild)
        # 2. NOW clear the global copies and push the empty list -> deletes the duplicates.
        self.bot.tree.clear_commands(guild=None)
        await self.bot.tree.sync()
        await ctx.send(f"✅ تم مزامنة {len(synced)} أمر (سيرفر) ومسح النسخ العامة")

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

    @commands.command()
    @prefix_cooldown()
    async def shutdown(self, ctx):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return
        await ctx.send("البوت راح يطفي الآن.")
        try:
            await self.bot.close()
        except Exception as e:
            _logger.error(f"Shutdown failed: {e}", exc_info=e)
            await ctx.send("❌ صار خطأ أثناء الإطفاء.")

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

    # Usage: !setstatus playing Valorant | !setstatus custom 🌙 Night Void | !setstatus clear
    @commands.command()
    @prefix_cooldown()
    async def setstatus(self, ctx, activity_type: str = None, *, text: str = None):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return

        if activity_type == "clear":
            self.status_text = None  # tells the loop to stop managing presence
            await self.bot.change_presence(activity=None)
            await ctx.send("✅ تم مسح الحالة")
            return

        if (activity_type not in ACTIVITY_TYPES and activity_type != "custom") or text is None:
            await ctx.send("❌ الاستخدام: `!setstatus <playing|watching|listening|competing|custom> <نص>` أو `!setstatus clear`")
            return

        # Update the shared state and reset the timer; the loop keeps it ticking after this.
        self.status_type = activity_type
        self.status_text = text
        self.status_since = discord.utils.utcnow()
        await self.bot.change_presence(activity=self._build_activity())
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
        
        # Usage: !say <الرسالة>  أو  !say #الروم <الرسالة>
    @commands.command()
    @prefix_cooldown()
    async def say(self, ctx, channel: Optional[discord.TextChannel] = None, *, message: str = None):
        if not await PermissionChecker.is_bot_owner(self.bot, ctx.author):
            await ctx.send("❌ هذا الأمر للبوت owner بس")
            return

        if message is None:
            await ctx.send("❌ الاستخدام: `!say [#الروم] <الرسالة>`")
            return

        target = channel or ctx.channel  # no channel given -> use the current one
        try:
            await target.send(message)
        except discord.Forbidden:
            await ctx.send(f"❌ ما عندي صلاحية أرسل في {target.mention}")
            return

        # Delete the invoking "!say ..." message so the bot looks like it spoke on its own.
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass  # no Manage Messages perm, or already gone -> just leave it

        if target != ctx.channel:
            await ctx.send(f"✅ تم الإرسال في {target.mention}")



async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))