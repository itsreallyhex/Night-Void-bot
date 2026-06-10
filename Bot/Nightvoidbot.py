import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from logger import setup_logger
logger = setup_logger("NightVoidBot")

load_dotenv()
token = os.getenv("NIGHTVOID_TOKEN")
guild_id = int(os.getenv("GUILD_ID"))

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
        await self.load_extension("cogs.adminprefix")
        await self.load_extension("cogs.adminslash")
        await self.load_extension("cogs.memberprefix")
        await self.load_extension("cogs.memberslash")
        self.tree.copy_global_to(guild=MY_GUILD)
        synced = await self.tree.sync(guild=MY_GUILD)
        logger.info(f"Synced {len(synced)} slash commands: {[c.name for c in synced]}")

bot = NightVoidBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to Discord!")

async def main():
    async with bot:
        await bot.start(token)

asyncio.run(main())
