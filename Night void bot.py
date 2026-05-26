import discord
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("NIGHTVOID_TOKEN") #Here you should put your bot token in the .env file
guild_id = int(os.getenv("GUILD_ID"))#Here you should put your server id in the .env file

#Intents
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

#events
@bot.event
async def on_ready():
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)
    print(f"{bot.user} has connected to Discord!")
#admin prefix
@bot.command()  
@commands.has_permissions(administrator=True)
async def howmanyMemberCheck(ctx):
    await ctx.send(f"يوجد حالياً {len(ctx.guild.members)} عضو في نايت فويد")

@bot.command()
@commands.has_permissions(administrator=True) 
async def howmanyMemberCheckOnline(ctx):
   online_members = [member for member in ctx.guild.members 
                  if (member.status != discord.Status.offline 
                  or member.mobile_status != discord.Status.offline)
                  and not member.bot]
   await ctx.send(f"يوجد حالياً {len(online_members)} عضو متصل في نايت فويد")

#Member prefix
@bot.command()
async def nightvoid(ctx):
    embed = discord.Embed(
        title="نايت فويد 🌙",
        description="بوت تم تطويره بواسطة <@904399821580943420>و<@1005827322844282951>. يهدف إلى تقديم تجربة فريدة وممتعة للأعضاء.",
        color=0x9B59B6
    )
    embed.add_field(name="الوظائف", value="إدارة الأدوار، التفاعل مع الأعضاء، معلومات الخادمب واكثر قادم.", inline=False)
    embed.add_field(name="واجاهت مشكلة اثناء استخدام البوت؟", value="تواصل مع الإدارة", inline=False)
    embed.set_footer(text="نايت فويد | Night Void")
    await ctx.send(embed=embed)

@bot.command()
async def prefix(ctx):
    embed = discord.Embed(
        title="البريفكس",
        description="البوت يستخدم البريفكس التالي: `!`",
        color=0x3498DB
    )
    embed.add_field(name="معلومات من البوت", value="!nightvoid", inline=True)
    embed.set_footer(text="نايت فويد | Night Void")
    await ctx.send(embed=embed)
#Admin commands
@bot.tree.command(name="ping", description="تحقق من تأخير البوت (ادمن فقط)")
async def ping(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ ما عندك صلاحية!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=" بونج",
        description=f"تأخير البوت: **{round(bot.latency * 1000)}ms**",
        color=0x2ECC71
    )
    embed.set_footer(text="نايت فويد | Night Void")
    await interaction.response.send_message(embed=embed)
#member commands
@bot.tree.command(name="serverinfo", description="يعطيك معلومات عن السيرفر")
async def serverinfo(interaction: discord.Interaction):
    human_count = len([m for m in interaction.guild.members if not m.bot])
    embed = discord.Embed(
        title=f"معلومات عن {interaction.guild.name}",
        description=(
            f"عدد الأعضاء: **{human_count}**\n"
            f"عدد الرولات: **{len(interaction.guild.roles)}**\n"
            f"صاحب السيرفر: **{interaction.guild.owner}**"
        ),
        color=0xE67E22
    )
    embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_footer(text="نايت فويد | Night Void")
    await interaction.response.send_message(embed=embed)

bot.run(token)
