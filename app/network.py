"""
Provides functions for establishing network locations and
communications, port and IP verification
"""
import traceback
import logging
from ipaddress import ip_address, IPv6Address, IPv4Address

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(filename='network.log', level=logging.INFO)

# Gets the external IP address where the server is running
# this assumes that the outbound IP after NAT and inbound IP
# before NAT are the same IP address.
#
# Unknown how this will behave in IPv6 environments, but the
# assumption is that it will work just the same as no NAT is
# used in IPv6 and the external IPv6 address will be the
# global address of the machine


def get_external_ip() -> str:
    """
    Gets the current external IP of where the app is running.
    This uses ifconfig.me and assumes it is not blocked or down.
    """
    try:
        response = requests.get('https://ifconfig.me/ip', timeout=5)
        server_ip = response.content.decode()
        logger.info(f'Discovered IP address is {server_ip}')
        return str(server_ip)

    except Exception:
        logger.error("External IP could not be found, ifconfig.me may be down or blocked")
        traceback.print_exc()
        raise

# Validates if the IP address given is valid


def valid_ip_address(ipaddress: int) -> int:
    """
    Checks if the IP address passed is a Valid IPv4 or IPv6 address
    """
    try:
        if isinstance(ip_address(ipaddress), (IPv4Address, IPv6Address)):
            return True
        else:
            return False

    except ValueError:
        logger.error("IP address is invalid")
        traceback.print_exc()
        raise

# Validates if the given port is in valid range


def valid_port(port: int) -> bool:
    """
    Checks if a given port is in the valid list of ranges for UDP ports
    """
    try:
        port = int(port)
        if port > 0 and port <= 65535:
            logger.info(f'PORT {port} is valid')
            return True
        raise ValueError(f'PORT {port} is not in valid range 1-65535')

    except Exception:
        logger.warning("PORT is not valid")
        traceback.print_exc()
        raise
