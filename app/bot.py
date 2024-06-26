"""
Discord bot that controls the power of a physical server
"""
import os
import sys
import json
import traceback
from asyncio import TimeoutError as asyncTimeoutError
from typing import List
import requests
import discord
from discord.ext import commands
import gamequery


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

# Defaulting POWERBOT_ROLE to "@everyone" unless set by the user
if env_defined("POWERBOT_ROLE"):
    POWERBOT_ROLE = os.environ["POWERBOT_ROLE"].split(",")
    # commands.has_any_role() takes either a role name as string,
    # or a role ID as integer. Can't just map() a mixed list.
    for i in range(0, len(POWERBOT_ROLE)):
        if POWERBOT_ROLE[i].isdigit():
            POWERBOT_ROLE[i] = int(POWERBOT_ROLE[i])
else:
    POWERBOT_ROLE = ['@everyone']

# Defaulting SUDO_ROLE to POWERBOT_ROLE unless set by the user
if env_defined("SUDO_ROLE"):
    SUDO_ROLE = os.environ["SUDO_ROLE"].split(",")
    for i in range(0, len(SUDO_ROLE)):
        if SUDO_ROLE[i].isdigit():
            SUDO_ROLE[i] = int(SUDO_ROLE[i])
else:
    SUDO_ROLE = POWERBOT_ROLE

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

def get_cooldown(ctx):
    """
    Returns the shared cooldown in seconds
    """
    boot_cd = bot.get_application_command(
        name="boot").get_cooldown_retry_after(ctx)
    reboot_cd = bot.get_application_command(
        name="reboot").get_cooldown_retry_after(ctx)
    shutdown_cd = bot.get_application_command(
        name="shutdown").get_cooldown_retry_after(ctx)
    return round(boot_cd + reboot_cd + shutdown_cd)


async def on_application_command_error(ctx, error):
    """
    Responds to a user calling a function that's currently on cooldown.
    """
    if isinstance(error, commands.CommandOnCooldown):
        cooldown = round(ctx.command.get_cooldown_retry_after(ctx))
        await ctx.respond(f'`/{ctx.command.name}` is currently on cooldown. '
                          f'Please wait another {cooldown}s before retrying, '
                          f'or retry with `/sudo {ctx.command.name}`.')

    elif isinstance(error, discord.errors.CheckFailure):
        # Since only one command can ever be on an individual cooldown,
        # addition works. One could get a cooldown via ctx.command.name
        # but we can't artificially set a cooldown, so this is the way
        # to link all commands to a shared CD
        cooldown = get_cooldown(ctx)
        sudoer = False
        for role in ctx.author.roles:
            if role.id in SUDO_ROLE or str(role.name) in SUDO_ROLE:
                sudoer = True
        if sudoer:
            await _sudo(ctx, command=ctx.command.name)
        else:
            await ctx.respond(f'`/{ctx.command.name}` is currently on cooldown. '
                              f'Please wait another {cooldown}s before retrying.')

    elif isinstance(error, commands.errors.MissingAnyRole):
        await ctx.respond(f'Sorry, you don\'t have the required role to use `/{ctx.command.name}`. '
                          f'Ask an adult to add you to one of these roles: '
                          f'`{", ".join(str(x) for x in POWERBOT_ROLE)}`'
                          f', or for `/sudo` commands: '
                          f'`{", ".join(str(x) for x in SUDO_ROLE)}`')

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
# https://github.com/Pycord-Development/pycord/issues/974
@commands.has_any_role(*POWERBOT_ROLE)
async def _boot(ctx):
    """
    Boots the server, returns an error message if any exception is caught
    """
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
# https://github.com/Pycord-Development/pycord/issues/974
@commands.has_any_role(*POWERBOT_ROLE)
async def _shutdown(ctx):
    """
    Shuts down the server under the condition of no player being online and 
    the function not being called via sudo
    """
    try:
        #TODO:myles - Add failed server query feedback to user
        is_anyone_active = gamequery.is_anyone_active()
        if is_anyone_active[0] and not ctx.author == 'sudo':
            await ctx.respond('Server can\'t be shut down, someone is online!')
        else:
            response = requests.get(SHUTDOWN_URL, timeout=2)
            if response.status_code == 200:
                game = discord.Activity(
                    name="Powering down...", type=discord.ActivityType.playing)
                await bot.change_presence(status=discord.Status.do_not_disturb, activity=game)
                await ctx.respond('Server shut down!')
    except Exception:
        await ctx.respond('Server is already offline or gameservers are down')
        traceback.print_exc()


@bot.slash_command(name="reboot", description="Reboots the game server")
@commands.cooldown(rate=1, per=float(COOLDOWN), type=commands.BucketType.guild)
@commands.check(check_cooldown)
# https://github.com/Pycord-Development/pycord/issues/974
@commands.has_any_role(*POWERBOT_ROLE)
async def _reboot(ctx):
    """
    reboots the server under the condition of no player being online and
    the function not being called via sudo
    """
    try:
        #TODO:myles - Add failed server query feedback to user
        is_anyone_active = gamequery.is_anyone_active()
        if is_anyone_active[0] and not ctx.author == 'sudo':
            await ctx.respond('Server can\'t be rebooted, someone is online!')
        else:
            response = requests.get(REBOOT_URL, timeout=2)
            if response.status_code == 200:
                game = discord.Activity(
                    name="Rebooting...", type=discord.ActivityType.playing)
                await bot.change_presence(status=discord.Status.streaming, activity=game)
                await ctx.respond('Server rebooting!')
    except Exception:
        await ctx.respond('Server is already offline')
        traceback.print_exc()


@bot.slash_command(name="sudo", description="Use commands regardless of their cooldown")
# https://github.com/Pycord-Development/pycord/issues/974
@commands.has_any_role(*SUDO_ROLE)
@discord.option(
    "command",
    description="Command to be run ignoring any cooldown.",
    choices=["boot", "reboot", "shutdown"]
)
async def _sudo(ctx, command):
    """
    Allows to bypass cooldowns that are usually placed upon power functions
    by resetting them all and then invoking the supplied command.
    Sets the command author to override the online check.
    """
    embed = discord.Embed(type="rich", colour=discord.Colour.red())
    embed.title = '<:warning:1043511363441537046>' \
                  ' WARNING <:warning:1043511363441537046>'
    cooldown = get_cooldown(ctx)
    if cooldown > 0:
        embed.description = f'Are you sure that you want to force `{command}`? ' \
                            f'It\'s still on cooldown for another {cooldown}s. ' \
                            'If yes, react with <:sos:1043671788007211108>.'
    else:
        embed.description = f'Are you sure that you want to force `{command}`? ' \
                            'If yes, react with <:sos:1043671788007211108>.'
    res = await ctx.respond(embed=embed)
    msg = await res.original_response()
    # default emojis need to be unicode
    await msg.add_reaction('\N{Squared SOS}')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '\N{Squared SOS}'
    try:
        await bot.wait_for('reaction_add', timeout=5.0, check=check)
    except asyncTimeoutError:
        await msg.clear_reactions()
    else:
        bot.get_application_command(name="boot").reset_cooldown(ctx)
        bot.get_application_command(name="reboot").reset_cooldown(ctx)
        bot.get_application_command(name="shutdown").reset_cooldown(ctx)
        ctx.author = 'sudo'
        await ctx.invoke(bot.get_application_command(command))
        await ctx.respond(f'`{command}` executed.')


@bot.slash_command(name="status",
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


@_boot.error
@_shutdown.error
@_reboot.error
@_sudo.error
async def _error(ctx, error):
    """
    Combined function to handle failed role checks,
    raises all further exceptions
    """
    await on_application_command_error(ctx, error)


bot.run(DISCORD_TOKEN)
