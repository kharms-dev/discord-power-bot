"""
Discord bot that controls the power of a physical server
"""
import traceback
from asyncio import TimeoutError as asyncTimeoutError
from typing import List
import requests
import discord
from cogs import config

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
        await ctx.respond(f'`/{ctx.command.name}` is currently on cooldown. '
                          f'Please wait another {cooldown}s before retrying.'
                          f'or retry with `/sudo {ctx.command.name}`.')
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
        await ctx.respond(f'`/{ctx.command.name}` is currently on cooldown. '
                          f'Please wait another {cooldown}s before retrying.'
                          f'or retry with `/sudo {ctx.command.name}`.')
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

@bot.slash_command(name="status",
                   description="Checks current power status of game server")
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
