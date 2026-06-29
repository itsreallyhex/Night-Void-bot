import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from logger import setup_logger

logger = setup_logger("NightVoidBot")

load_dotenv()
token = os.getenv("BOT_TOKEN")
raw_guild_id = os.getenv("GUILD_ID")

if not token:
    raise ValueError("BOT_TOKEN is not set in environment variables")
if not raw_guild_id:
    raise ValueError("GUILD_ID is not set in environment variables")

guild_id = int(raw_guild_id)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.guilds = True
intents.reactions = True
intents.typing = True
intents.dm_messages = True
intents.dm_reactions = True

MY_GUILD = discord.Object(id=guild_id)

class NightVoidBot(commands.Bot):
    async def setup_hook(self):
        extensions = [
            "cogs.adminprefix",
            "cogs.adminslash",
            "cogs.memberprefix",
            "cogs.memberslash",
            "cogs.OwnerCommands",
            "cogs.honeypot",
        ]
        for ext in extensions:
            try:
                await self.load_extension(ext)
            except Exception as e:
                logger.error(f"Failed to load extension {ext}: {e}")

        self.tree.copy_global_to(guild=MY_GUILD)
        synced = await self.tree.sync(guild=MY_GUILD)
        logger.info(f"Synced {len(synced)} slash commands: {[c.name for c in synced]}")

        # Global slash command error handler
        async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            if isinstance(error, app_commands.CommandOnCooldown):
                await interaction.response.send_message(
                    f"⏱️ انتظر {error.retry_after:.1f} ثانية قبل ما تستخدم الأمر ثاني مرة.",
                    ephemeral=True
                )
            elif isinstance(error, app_commands.MissingPermissions):
                await interaction.response.send_message("❌ ما عندك صلاحية لهذا الأمر.", ephemeral=True)
            else:
                logger.error(f"Unhandled slash command error in '{interaction.command.name if interaction.command else 'unknown'}': {error}", exc_info=error)
                msg = "❌ صار خطأ غير متوقع، حاول مرة ثانية."
                if not interaction.response.is_done():
                    await interaction.response.send_message(msg, ephemeral=True)
                else:
                    await interaction.followup.send(msg, ephemeral=True)

        self.tree.on_error = on_tree_error

bot = NightVoidBot(command_prefix="!", intents=intents)
bot.start_time = discord.utils.utcnow()
bot.main_guild = MY_GUILD


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to Discord!")

# Global prefix command error handler
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands silently
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ ناقص argument: `{error.param.name}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ قيمة خاطئة في الأمر، تحقق من المدخلات.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏱️ انتظر {error.retry_after:.1f} ثانية قبل ما تستخدم الأمر ثاني مرة.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ ما عندك صلاحية لهذا الأمر.")
    else:
        logger.error(f"Unhandled prefix command error in '{ctx.command}': {error}", exc_info=error)
        await ctx.send("❌ صار خطأ غير متوقع، حاول مرة ثانية.")

async def main():
    async with bot:
        try:
            await bot.start(token)
        except discord.LoginFailure:
            logger.critical("Invalid Discord token. Check BOT_TOKEN.")
        except Exception as e:
            logger.critical(f"Bot crashed during startup: {e}", exc_info=e)

asyncio.run(main())
