"""
Discord bot that controls the power of a physical server
"""
import traceback
import requests
import discord
from cogs import config


intents = discord.Intents.default()
DESC = "Bot to control the power to physical game server"
bot = discord.Bot(description=DESC, intents=intents)


@bot.event
async def on_ready():
    """
    Runs on bot boot and updates the status of the bot in Discord
    """
    game = discord.Activity(
        name="Standing by...", type=discord.ActivityType.playing)
    await bot.change_presence(status=discord.Status.idle, activity=game)
    print('Connected to API')


@bot.slash_command(name="status", description="Checks current power status of game server")
async def _status(ctx):
    try:
        response = requests.get(config.LIVENESS_URL, timeout=2)
        if response.status_code == 200:
            game = discord.Activity(
                name="Server online", type=discord.ActivityType.playing)
            await bot.change_presence(status=discord.Status.online, activity=game)
            await ctx.respond('Server is up!')
    except requests.exceptions.RequestException:
        game = discord.Activity(
            name="Server offline", type=discord.ActivityType.playing)
        await bot.change_presence(status=discord.Status.idle, activity=game)
        await ctx.respond('Server is offline')
        print("Server host is offline")
        traceback.print_exc()

bot.load_extension('cogs.poweractions')

bot.run(config.DISCORD_TOKEN)
