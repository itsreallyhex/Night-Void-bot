import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

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

bot = commands.Bot(command_prefix="!", intents=intents)
MY_GUILD = discord.Object(id=guild_id)

@bot.event
async def on_ready():
    await bot.load_extension("Bot.cogs.adminprefix")
    await bot.load_extension("Bot.cogs.adminslash")
    await bot.load_extension("Bot.cogs.memberprefix")
    await bot.load_extension("Bot.cogs.memberslash")
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)
    print(f"{bot.user} has connected to Discord!")

async def main():
    async with bot:
        await bot.start(token)

asyncio.run(main())
