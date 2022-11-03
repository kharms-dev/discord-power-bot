"""
Queries SteamQuery, DCS and SpaceEngineers instances
"""
import traceback
from steam import SteamQuery
import network
from servers import Server


def get_players(ipaddress: int, port: int, password="") -> dict:
    """
    Returns a dict with the current number of players connected
    to the server as well as the max players supported
    """
    try:
        server = _steam_server_connection(server_ip=ipaddress, port=port)
        server_state = _lint_steamquery_output(server.query_server_info())
        return {"current_players": server_state["players"],
                "max_players": server_state["max_players"]}

    except Exception:
        print("Could not get server info")
        traceback.print_exc()
        raise


def get_players_details(ipaddress: int, port: int, password="") -> list:
    """
    Returns a list with all current player objects containing
    names, scores and durations on the server
    """
    try:
        server = _steam_server_connection(server_ip=ipaddress, port=port)
        player_info = _lint_steamquery_output(server.query_player_info())
        return player_info

    except Exception:
        print("Could not get player info")
        traceback.print_exc()
        raise

# Creates and returns server connection object


def _steam_server_connection(server_ip: int, port: int) -> object:
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
