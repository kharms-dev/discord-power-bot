import os
import sys


def env_defined(key):
    """
    Checks if a given env var key is defined in the OS environment
    """
    return key in os.environ and len(os.environ[key]) > 0

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
