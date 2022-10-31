"""
Provides Server data class type for storing game
server config info
"""
import traceback
import json
from dataclasses import dataclass
from enum import Enum


class ServerType(str, Enum):
    """
    Enum for storing supported backend server types
    """
    STEAM = 'STEAM'
    DCS = 'DCS'
    SPACE_ENGINEERS = 'SPACE_ENGINNERS'


@dataclass
class Server:
    """
    Object that stores a given game server
    configuration
    """
    name: str
    ip_address: str
    port: int
    password: str
    server_type: ServerType


server_list = {}


def add_server(name, ip_address, port, server_type, password=""):
    """
    Adds a server to the actively monitored list
    """
    try:
        if not name in server_list:
            if server_type in ServerType.__members__:
                server = Server(name=name, ip_address=ip_address,
                                port=port, password=password, server_type=ServerType[server_type])
                server_list[name] = server
                return server
            raise TypeError(f"Server type '{server_type}' is invalid")
        raise ValueError("Server name already taken")
    except Exception:
        print("Failed to add server")
        traceback.print_exc()
        raise


def delete_server(name):
    """
    Deletes a server from the actively monitored list
    """
    server_list.pop(name)


def update_server(name, server):
    """
    Updates a server entry in the bot's monitoring list
    Side note: this is essentially the same op as add_server
    but without the duplicate key check to allow for overwrites
    """
    server_list[name] = server


def get_server(name):
    """
    Returns server object based on server name
    """
    return server_list.get(name)


def list_servers():
    """
    Lists servers currently monitored by the bot
    """
    print(server_list)


def save_servers():
    """
    Saves out server config to disk as json
    """
    server_serialised = []
    for server in server_list.values():
        print(server.server_type.value)
        print(server.__dict__)
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
        print("Couldn't load settings into bot")
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
        print("Failed to save settings to disk")
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
        print("Settings file not found")
        raise
    except Exception:
        print("Failed to load settings from disk")
        traceback.print_exc()
        raise
