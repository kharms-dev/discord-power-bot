"""
Discord bot that controls the power of a physical server
"""
import os
import sys
import json
import traceback
import requests
import discord


def env_defined(key):
    """
    Checks if a given env var key is defined in the OS environment
    """
    return key in os.environ and len(os.environ[key]) > 0


DISCORD_CHANNEL = []
# env variables are defaults, if no config file exists it'll be created.
# If no env is set, stop the bot
if not env_defined("DISCORD_TOKEN"):
    print("Missing bot token from .env")
    sys.exit()
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

if not env_defined("WOL_URL"):
    print("Missing wake on lan URL from .env")
    sys.exit()
WOL_URL = os.environ["WOL_URL"]

if not env_defined("SHUTDOWN_URL"):
    print("Missing shutdown URL from .env")
    sys.exit()
SHUTDOWN_URL = os.environ["SHUTDOWN_URL"]

if not env_defined("REBOOT_URL"):
    print("Missing liveness URL from .env")
    sys.exit()
REBOOT_URL = os.environ["REBOOT_URL"]

if not env_defined("LIVENESS_URL"):
    print("Missing liveness URL from .env")
    sys.exit()
LIVENESS_URL = os.environ["LIVENESS_URL"]

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


@ bot.slash_command(name="boot", description="Boots the game server")
async def _boot(ctx):
    try:
        response = requests.get(WOL_URL, timeout=2)
        jsonresponse = json.loads(response.content.decode())
        if jsonresponse.get('success') is True:
            game = discord.Activity(
                name="Booting...", type=discord.ActivityType.playing)
            await bot.change_presence(status=discord.Status.online, activity=game)
            await ctx.respond('Server booted!')
    except Exception:
        await ctx.respond('Something went wrong, have an adult check the logs')
        traceback.print_exc()


@ bot.slash_command(name="shutdown", description="Shuts down the game server")
async def _shutdown(ctx):
    try:
        response = requests.get(SHUTDOWN_URL, timeout=2)
        if response.status_code == 200:
            game = discord.Activity(
                name="Powering down...", type=discord.ActivityType.playing)
            await bot.change_presence(status=discord.Status.do_not_disturb, activity=game)
            await ctx.respond('Server shut down!')
    except Exception:
        await ctx.respond('Server is already offline')
        traceback.print_exc()


@ bot.slash_command(name="reboot", description="Reboots the game server")
async def _reboot(ctx):
    try:
        response = requests.get(REBOOT_URL, timeout=2)
        if response.status_code == 200:
            game = discord.Activity(
                name="Rebooting...", type=discord.ActivityType.playing)
            await bot.change_presence(status=discord.Status.streaming, activity=game)
            await ctx.respond('Server rebooting!')
    except Exception:
        await ctx.respond('Server is already offline')
        traceback.print_exc()


@ bot.slash_command(name="status", description="Checks current power status of game server")
async def _status(ctx):
    try:
        response = requests.get(LIVENESS_URL, timeout=2)
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

bot.run(DISCORD_TOKEN)
