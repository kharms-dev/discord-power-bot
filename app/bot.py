"""
Discord bot that controls the power of a physical server
"""
import os
import sys
import json
import traceback
import requests
import discord
from typing import List
from discord.ext import commands


def env_defined(key):
    """
    Checks if a given env var key is defined in the OS environment
    """
    return key in os.environ and len(os.environ[key]) > 0


DISCORD_CHANNEL: List[str] = []

# env variables are defaults, if no config file exists it'll be created.
# If no env is set, stop the bot
try:
    DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
    WOL_URL = os.environ["WOL_URL"]
    SHUTDOWN_URL = os.environ["SHUTDOWN_URL"]
    REBOOT_URL = os.environ["REBOOT_URL"]
    LIVENESS_URL = os.environ["LIVENESS_URL"]
except KeyError as e:
    print(f"Missing {str(e)} token from .env.")
    sys.exit()

# Defaulting COOLDOWN to 300s unless set by the user
if env_defined("COOLDOWN"):
    COOLDOWN: int = int(os.environ["COOLDOWN"])
else:
    COOLDOWN: int = 300

intents = discord.Intents.default()
DESC = "Bot to control the power to physical game server"
bot = discord.Bot(description=DESC, intents=intents)


def check_cooldown(ctx):
    """
    Each of boot, shutdown, restart triggers a cooldown for itself.
    This function is designed to link their cooldowns to avoid hangups.
    """
    if ctx.command.name in ["boot", "reboot", "shutdown"]:
        boot_cd = bot.get_application_command(name="boot").is_on_cooldown(ctx)
        reboot_cd = bot.get_application_command(
            name="reboot").is_on_cooldown(ctx)
        shutdown_cd = bot.get_application_command(
            name="shutdown").is_on_cooldown(ctx)
        if boot_cd or reboot_cd or shutdown_cd:
            return False
    return True


async def on_application_command_error(ctx, error):
    """
    Responds to a user calling a function that's currently on cooldown.
    """
    if isinstance(error, commands.CommandOnCooldown):
        cooldown = round(ctx.command.get_cooldown_retry_after(ctx))
        await ctx.respond(f"`/{ctx.command.name}` is currently on cooldown. "
                          f"Please wait another {cooldown}s before retrying.")
    elif isinstance(error, discord.errors.CheckFailure):
        boot_cd = bot.get_application_command(
            name="boot").get_cooldown_retry_after(ctx)
        reboot_cd = bot.get_application_command(
            name="reboot").get_cooldown_retry_after(ctx)
        shutdown_cd = bot.get_application_command(
            name="shutdown").get_cooldown_retry_after(ctx)
        # Since only one command can ever be on an individual cooldown,
        # addition works
        cooldown = round(boot_cd + reboot_cd + shutdown_cd)
        await ctx.respond(f"`/{ctx.command.name}` is currently on cooldown. "
                          f"Please wait another {cooldown}s before retrying.")
    else:
        raise error  # Here we raise other errors to ensure they aren't ignored


@bot.event
async def on_ready():
    """
    Runs on bot boot and updates the status of the bot in Discord
    """
    game = discord.Activity(
        name="Standing by...", type=discord.ActivityType.playing)
    await bot.change_presence(status=discord.Status.idle, activity=game)
    print('Connected to API')


@bot.slash_command(name="boot", description="Boots the game server")
@commands.cooldown(rate=1, per=float(COOLDOWN), type=commands.BucketType.guild)
@commands.check(check_cooldown)
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


@bot.slash_command(name="shutdown", description="Shuts down the game server")
@commands.cooldown(rate=1, per=float(COOLDOWN), type=commands.BucketType.guild)
@commands.check(check_cooldown)
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


@bot.slash_command(name="reboot", description="Reboots the game server")
@commands.cooldown(rate=1, per=float(COOLDOWN), type=commands.BucketType.guild)
@commands.check(check_cooldown)
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


@_boot.error
@_shutdown.error
@_reboot.error
async def _error(ctx, error):
    await on_application_command_error(ctx, error)


@ bot.slash_command(name="status",
                    description="Checks current power status of game server")
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
