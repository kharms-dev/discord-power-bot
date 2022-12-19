"""
Queries SteamQuery, DCS and SpaceEngineers instances
"""
import traceback
import logging
from steam import SteamQuery
import network
from servers import Server, ServerType, list_servers, get_server


def is_anyone_active() -> bool:
    """
    Checks all known servers for users currently logged in
    returns a bool
    """
    try:
        player_count = 0
        for server in list_servers():
            server = get_server(server)
            player_count += get_players(server).get('current_players')
        if player_count > 0:
            return True
        else:
            return False
    except:
        logging.error("Couldn't query servers for active players")
        traceback.print_exc()
        raise


def get_players(server: Server) -> dict:
    """
    Returns a dict with the current number of players connected
    to the server as well as the max players supported
    """
    if server['server_type'] is ServerType.STEAM:
        try:
            steamquery = _steam_server_connection(
                server_ip=str(server['ip_address']), port=server['port'])
            server_state = _lint_steamquery_output(
                steamquery.query_server_info())
            return {"current_players": server_state["players"],
                    "max_players": server_state["max_players"]}

        except Exception:
            print("Could not get server info")
            traceback.print_exc()
            raise
    elif server['server_type'] is ServerType.SPACE_ENGINEERS:
        return {"current_players": 0,
                "max_players": 0}

    elif server['server_type'] is ServerType.DCS:
        return {"current_players": 0,
                "max_players": 0}

    else:
        print(f'Cannot query unrecognised server type {server_type}')


def get_players_details(server: Server) -> list:
    """
    Returns a list with all current player objects containing
    names, scores and durations on the server
    """
    if server['server_type'] is ServerType.STEAM:
        try:
            steamquery = _steam_server_connection(
                server_ip=str(server['ip_address']), port=server['port'])
            player_info = _lint_steamquery_output(
                steamquery.query_player_info())
            return player_info

        except Exception:
            print("Could not get player info")
            traceback.print_exc()
            raise
    elif server['server_type'] is ServerType.SPACE_ENGINEERS:
        pass

    elif server['server_type'] is ServerType.DCS:
        pass

    else:
        print(f'Cannot query unrecognised server type {server_type}')

# Creates and returns server connection object


def _steam_server_connection(server_ip: str, port: int) -> object:
    """
    Creates a steam query server connection object and passes it back.
    """
    try:
        # Check if IP address is valid
        if not network.valid_ip_address(server_ip):
            raise ValueError("IP Address Invalid")

        # Check if port is valid
        if not network.valid_port(port):
            raise ValueError("PORT environment variable is invalid")

        # Construct SteamQuery session
        print(f'Connecting to {server_ip}:{port}')
        server = SteamQuery(server_ip, port)
        return server

    except Exception:
        print("Unable to connect to server")
        traceback.print_exc()
        raise


def _lint_steamquery_output(query) -> object:
    """
    Checks if SteamQuery output should have been an exception
    and if so raises one, kill me
    """
    # SteamQuery lib returns errors as strings, so need to
    # check if "error" key is present to detect exceptions
    # when errored, it is always passed back as a dict
    #
    # If the query is a list, then it is a valid response
    # in any case
    if isinstance(query, list):
        return query
    else:
        try:
            if "error" in query.keys():
                raise ConnectionError(str(query))
            else:
                return query
        except Exception:
            print("Error passed back from SteamQuery")
            traceback.print_exc()
            raise
