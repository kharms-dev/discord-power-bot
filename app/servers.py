"""
Provides Server data class type for storing game
server config info
"""
import traceback
import json
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.WARN)


class ServerType(str, Enum):
    """
    Enum for storing supported backend server types
    """
    STEAM = 'STEAM'
    DCS = 'DCS'
    SPACE_ENGINEERS = 'SPACE_ENGINEERS'


@dataclass
class Server:
    """
    Object that stores a given game server
    configuration
    """
    name: str
    ip_address: str
    port: int
    server_type: ServerType
    password: str


server_list = {}


def add_server(name, ip_address, port, server_type, password=""):
    """
    Adds a server to the actively monitored list
    """
    try:
        if not name in server_list:
            if server_type in ServerType.__members__:
                server = Server(name=name, ip_address=ip_address,
                                port=port, server_type=ServerType[server_type], password=password)
                server_list[name] = server
                return server
            raise TypeError(f"Server type '{server_type}' is invalid")
        raise ValueError("Server name already taken")
    except Exception:
        logging.error("Failed to add server")
        traceback.print_exc()
        raise


def delete_server(name):
    """
    Deletes a server from the actively monitored list
    """
    try:
        return server_list.pop(name)
    except KeyError:
        logging.error(f"Failed to delete server, '{name}' does not exist.")
        traceback.print_exc()
        raise


def update_server(name, server):
    """
    Updates a server entry in the bot's monitoring list
    Side note: this is essentially the same op as add_server
    but without the duplicate key check to allow for overwrites
    """
    try:
        server_list[name] = server
        return True
    except Exception:
        logging.error("Failed to update server")
        traceback.print_exc()
        raise


def get_server(name):
    """
    Returns server object based on server name
    """
    return server_list.get(name)


def list_servers():
    """
    Lists servers currently monitored by the bot
    """
    return server_list


def save_servers():
    """
    Saves out server config to disk as json
    """
    server_serialised = []
    for server in server_list.values():
        server_serialised.append(server.__dict__)
    _save_settings(server_serialised)


def load_servers():
    """
    Loads servers from disk, overwrites any existing entries of the same name
    """
    servers = _load_settings()
    try:
        for server in servers:
            if not server['server_type'] in ServerType.__members__:
                raise TypeError(
                    f"Server type: '{server['server_type']}' \
                       for server '{server['name']}' is invalid")
            server_obj = Server(name=server['name'], ip_address=server['ip_address'],
                                port=server['port'], password=server['password'],
                                server_type=ServerType(server['server_type']))
            update_server(server['name'], server_obj)
    except Exception:
        logging.error("Couldn't load settings into bot")
        traceback.print_exc()
        raise


def _save_settings(jsonstring):
    """
    Writes out server config settings to disk in json
    """
    try:
        with open('servers.json', 'w', encoding='utf8') as configfile:
            json.dump(jsonstring, configfile, indent=4, sort_keys=True)
    except Exception:
        logging.error("Failed to save settings to disk")
        traceback.print_exc()
        return 0
    return 1


def _load_settings():
    """
    Writes out server config settings to disk in json
    """
    try:
        with open('servers.json', 'r', encoding='utf8') as configfile:
            jsonstring = json.load(configfile)
            return jsonstring
    except FileNotFoundError:
        logging.error("Settings file not found")
        raise
    except Exception:
        logging.error("Failed to load settings from disk")
        traceback.print_exc()
        raise
