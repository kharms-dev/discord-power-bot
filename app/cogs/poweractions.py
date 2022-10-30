import json
import traceback
import requests
import discord
from discord.ext import commands
import config


class PowerActions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def actions(self, ext):
        pass

    @actions.slash_command(name="boot", description="Boots the game server")
    async def _boot(self, ctx):
        try:
            response = requests.get(config.WOL_URL, timeout=2)
            jsonresponse = json.loads(response.content.decode())
            if jsonresponse.get('success') is True:
                game = discord.Activity(
                    name="Booting...", type=discord.ActivityType.playing)
                await self.bot.change_presence(status=discord.Status.online, activity=game)
                await ctx.respond('Server booted!')
        except Exception:
            await ctx.respond('Something went wrong, have an adult check the logs')
            traceback.print_exc()

    @actions.slash_command(name="shutdown", description="Shuts down the game server")
    async def _shutdown(self, ctx):
        try:
            response = requests.get(config.SHUTDOWN_URL, timeout=2)
            if response.status_code == 200:
                game = discord.Activity(
                    name="Powering down...", type=discord.ActivityType.playing)
                await self.bot.change_presence(status=discord.Status.do_not_disturb, activity=game)
                await ctx.respond('Server shut down!')
        except Exception:
            await ctx.respond('Server is already offline')
            traceback.print_exc()

    @actions.slash_command(name="reboot", description="Reboots the game server")
    async def _reboot(self, ctx):
        try:
            response = requests.get(config.REBOOT_URL, timeout=2)
            if response.status_code == 200:
                game = discord.Activity(
                    name="Rebooting...", type=discord.ActivityType.playing)
                await self.bot.change_presence(status=discord.Status.streaming, activity=game)
                await ctx.respond('Server rebooting!')
        except Exception:
            await ctx.respond('Server is already offline')
            traceback.print_exc()


def setup(bot):
    bot.add_cog(PowerActions(bot))
