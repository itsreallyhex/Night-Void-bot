import os
import json
import asyncio
from datetime import timedelta

import discord
from discord.ext import commands
from discord import app_commands

from utilities import PermissionChecker, EphemeralReply, slash_cooldown
from logger import setup_logger

_logger = setup_logger("NightVoid.Honeypot")

# Warning DM (Saudi dialect). Sent to the suspected-compromised account.
WARNING_DM = (
    "فيه احتمال إن حسابك متهكر. عشان تأمن نفسك، غيّر كلمات السر وسوّي تسجيل خروج "
    "من كل أجهزتك الحين. ولو أنت اللي كتبت بنفسك في سيرفر نايت فويد، "
    "فالتحذير هذا ما يخصك."
)

# Counter is persisted across restarts. Default location is next to the Bot
# package (Bot/honeypot_stats.json). On hosts with an ephemeral filesystem
# (e.g. Railway) set HONEYPOT_STATS_PATH to a persistent volume mount so the
# count survives redeploys. __file__ -> Bot/cogs/Honypot.py, so go up two levels.
_STATS_PATH = os.getenv("HONEYPOT_STATS_PATH") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "honeypot_stats.json",
)


def _parse_int(value, default=0):
    """Best-effort int parse for env vars; returns default on missing/garbage."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_id_list(value):
    """Parse a comma-separated list of IDs from env into a set of ints."""
    if not value:
        return set()
    ids = set()
    for chunk in value.split(","):
        chunk = chunk.strip()
        if chunk:
            ids.add(_parse_int(chunk, 0))
    ids.discard(0)
    return ids


# THIS COG IS THE QUARANTINE / HONEYPOT CHANNEL GUARD.
# Any non-exempt message in the protected channel = the account is treated as
# compromised: timeout + delete + DM warning. The whole point is that no normal
# human should ever post there, so a post is a strong "hacked spammer" signal.
class Honeypot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # --- Configuration (all from environment) ---
        self.protected_channel_id = _parse_int(os.getenv("PROTECTED_CHANNEL_ID"))
        self.log_channel_id = _parse_int(os.getenv("LOG_CHANNEL_ID"))
        self.safe_role_ids = _parse_id_list(os.getenv("SAFE_ROLE_IDS"))
        self.whitelist_user_ids = _parse_id_list(os.getenv("WHITELIST_USER_IDS"))
        self.preserved_message_id = _parse_int(os.getenv("PRESERVED_MESSAGE_ID"))
        self.timeout_minutes = _parse_int(os.getenv("TIMEOUT_DURATION_MINUTES"), 1440)

        # Lock guards the JSON read-modify-write so two near-simultaneous spam
        # messages can't clobber each other's count.
        self._stats_lock = asyncio.Lock()
        self.timeout_count = self._load_count()

        if not self.protected_channel_id:
            _logger.warning("PROTECTED_CHANNEL_ID not set — honeypot is inactive.")
        else:
            _logger.info(
                "Honeypot active on channel %s | timeout=%dm | safe_roles=%s",
                self.protected_channel_id, self.timeout_minutes, self.safe_role_ids,
            )

    # ----- Persistence -----
    def _load_count(self) -> int:
        try:
            with open(_STATS_PATH, "r", encoding="utf-8") as f:
                return int(json.load(f).get("timeout_count", 0))
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            return 0

    async def _save_count(self):
        async with self._stats_lock:
            self.timeout_count += 1
            try:
                with open(_STATS_PATH, "w", encoding="utf-8") as f:
                    json.dump({"timeout_count": self.timeout_count}, f)
            except OSError as e:
                _logger.error("Failed to persist honeypot count: %s", e)

    # ----- Exemption -----
    def _is_exempt(self, member: discord.Member) -> bool:
        # Exemption is checked BEFORE any action — never touch a mod/bot.
        # Exact-match only: a member is exempt if they are the bot, whitelisted,
        # the guild owner, an administrator, or hold one of the EXACT roles listed
        # in SAFE_ROLE_IDS. Role hierarchy/position is intentionally NOT used, so
        # a verified/member role won't accidentally exempt regular members.
        if member.bot:
            return True
        if member.id == self.bot.user.id:
            return True
        if member.id in self.whitelist_user_ids:
            return True
        if PermissionChecker.is_guild_owner(member) or PermissionChecker.is_admin(member):
            return True
        if self.safe_role_ids & {r.id for r in member.roles}:
            return True
        return False

    # ----- Logging -----
    async def _log_event(self, member: discord.Member, content: str):
        if not self.log_channel_id:
            return
        channel = self.bot.get_channel(self.log_channel_id)
        if channel is None:
            _logger.warning("LOG_CHANNEL_ID %s not found.", self.log_channel_id)
            return
        embed = discord.Embed(
            title=" تايم اوت من غرفة الحماية",
            color=0xE74C3C,
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="العضو", value=f"{member} ({member.mention})", inline=False)
        embed.add_field(name="الايدي", value=str(member.id), inline=True)
        embed.add_field(name="المدة", value=f"{self.timeout_minutes} دقيقة", inline=True)
        # Message content can be empty (image/embed only) — guard the field.
        embed.add_field(
            name="الرسالة",
            value=(content[:1024] if content else "*(ما فيه نص)*"),
            inline=False,
        )
        try:
            await channel.send(embed=embed)
        except discord.HTTPException as e:
            _logger.error("Failed to write honeypot log: %s", e)

    # ----- Main guard -----
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Only act inside the configured protected channel.
        if not self.protected_channel_id or message.channel.id != self.protected_channel_id:
            return
        # Ignore DMs / webhooks / anything without a real guild member author.
        if message.guild is None or not isinstance(message.author, discord.Member):
            return
        # Never delete the owner's preserved pin.
        if self.preserved_message_id and message.id == self.preserved_message_id:
            return
        # EXEMPTION FIRST — bots, mods, whitelist, etc. are left untouched.
        if self._is_exempt(message.author):
            return

        member = message.author
        content = message.content  # capture before deletion

        # 1) Timeout using Discord's native feature (communication_disabled_until).
        try:
            await member.timeout(
                timedelta(minutes=self.timeout_minutes),
                reason="كتب في غرفة الحماية بسيرفر نايت فويد (احتمال حساب متهكر).",
            )
            timed_out = True
        except discord.Forbidden:
            # Missing Moderate Members perm or target is above the bot — skip silently.
            _logger.error("No permission to timeout %s (%s).", member, member.id)
            timed_out = False
        except discord.HTTPException as e:
            _logger.error("Timeout API error for %s: %s", member.id, e)
            timed_out = False

        # 2) Delete the triggering message.
        try:
            await message.delete()
        except discord.Forbidden:
            _logger.error("No permission to delete message in protected channel.")
        except discord.NotFound:
            pass  # already gone

        if not timed_out:
            return  # nothing to record/notify if the core action failed

        # 3) Persist the counter.
        await self._save_count()

        # 4) DM the user — failures (closed DMs) must not crash the handler.
        try:
            await member.send(WARNING_DM)
        except (discord.Forbidden, discord.HTTPException):
            _logger.info("Could not DM warning to %s (%s) — DMs closed.", member, member.id)

        # 5) Log the event.
        await self._log_event(member, content)
        _logger.info("Timed out %s (%s) | total=%d", member, member.id, self.timeout_count)

    # ----- Stats command -----
    @app_commands.command(name="stats", description="يعطيك عدد التايم اوت اللي طلعتها غرفة الحماية (ادمن فقط)")
    @slash_cooldown()
    async def stats(self, interaction: discord.Interaction):
        if not PermissionChecker.is_admin(interaction.user):
            await EphemeralReply.send(interaction, "❌ ما عندك صلاحية!")
            return
        await interaction.response.send_message(
            f"🔒 إجمالي التايم اوت: {self.timeout_count}"
        )


async def setup(bot):
    await bot.add_cog(Honeypot(bot))
