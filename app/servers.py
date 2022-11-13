"""
Provides Server data class type for storing game
server config info
"""
import traceback
import json
import logging
from enum import Enum
from marshmallow import Schema, fields, validate

logging.basicConfig(level=logging.WARN)


class ServerType(str, Enum):
    """
    Enum for storing supported backend server types
    """
    STEAM = 'STEAM'
    DCS = 'DCS'
    SPACE_ENGINEERS = 'SPACE_ENGINEERS'


class Server(Schema):
    """
    Object that stores a given game server
    configuration
    """
    name = fields.Str()
    ip_address = fields.IP()
    port = fields.Int(validate=validate.Range(1, 65535))
    password = fields.Str()
    server_type = fields.Enum(ServerType)


server_list = {}


def add_server(name: str, ip_address: str, port: int, server_type: str, password: str = "") -> Server:
    """
    Adds a server to the actively monitored list
    """
    try:
        if not name in server_list:
            server_info = {
                'name': name,
                'ip_address': ip_address,
                'port': port,
                'server_type': server_type,
                'password': password
            }
            server = Server().load(server_info)
            server_list[name] = server
            return server
        raise ValueError("Server name already taken")
    except Exception:
        logging.error("Failed to add server")
        traceback.print_exc()
        raise


def delete_server(name):
    """
    Deletes a server from the actively monitored list
    """
    if name == '*':
        server_list.clear()
    else:
        server_list.pop(name)


def update_server(name: str, server_info: dict):
    """
    Updates a server entry in the bot's monitoring list
    Side note: this is essentially the same op as add_server
    but without the duplicate key check to allow for overwrites
    """
    try:
        schema = Server()
        server = schema.load(server_info)
        server_list[name] = server
    except ValueError:
        logging.error("Failed to update server")
        traceback.print_exc()


def get_server(name):
    """
    Returns server object based on server name
    """
    return server_list.get(name)


def list_servers() -> dict:
    """
    Lists servers currently monitored by the bot
    """
    return server_list


def save_servers():
    """
    Saves out server config to disk as json
    """
    server_serialised = []
    schema = Server()
    for server in server_list.values():
        server_serialised.append(schema.dump(server))
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
            update_server(server['name'], server)
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


def _load_settings() -> dict:
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
