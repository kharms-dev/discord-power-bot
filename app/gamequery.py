"""
Queries SteamQuery, DCS, Minecraft and SpaceEngineers instances
"""
import traceback
import logging
from steam import SteamQuery #SteamQuery
from mcstatus import JavaServer #Minecraft Java
from mcstatus import BedrockServer #Minecraft Bedrock
from vrage_api.vrage_api import VRageAPI #SpaceEngineers
import network
from servers import Server, ServerType, list_servers, load_servers, get_server


def is_anyone_active() -> bool:
    """
    Checks all known servers for users currently logged in
    returns a bool
    """
    try:
        player_count = 0
        if list_servers() == {}:
            load_servers()
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
            print("Could not get ArmA server info")
            traceback.print_exc()
            raise

    elif server['server_type'] is ServerType.SPACE_ENGINEERS:
        try:
            server_api_address = "http://" + \
                str(server['ip_address']) + ":" + str(server['port'])
            api = VRageAPI(url=server_api_address, token=server['password'])
            players = api.get_players()
            server_ping = api.get_server_ping()
            server_info = api.get_server_info()

            if server_ping["data"]["Result"] == "Pong":
                server_live = True
            else:
                server_live = False

            print(f"Server live: {server_live}")
            print(server_info["data"])
            # Saves the current session state
            # api.query('/vrageremote/v1/session','patch')
            player_count = server_info["data"]["Players"]

            for player in players["data"]["Players"]:
                print(player["SteamID"], player["DisplayName"])

            return {"current_players": player_count, "max_players": 99}

        except Exception:
            print("Could not get Space Engineers server info")
            traceback.print_exc()
            raise

    elif server['server_type'] is ServerType.MINECRAFT_JAVA:
        try:
            server = JavaServer(str(server['ip_address']), server['port'])
            status = server.status()
            return {"current_players": status.players.online,
                    "max_players": status.players.max}

        except Exception:
            print("Could not get Minecraft JE server info")
            traceback.print_exc()
            raise

    elif server['server_type'] is ServerType.MINECRAFT_BEDROCK:
        try:
            server = BedrockServer(str(server['ip_address']), server['port'])
            status = server.status()
            return {"current_players": status.players.online,
                    "max_players": status.players.max}

        except Exception:
            print("Could not get Minecraft Bedrock server info")
            traceback.print_exc()
            raise

    elif server['server_type'] is ServerType.DCS:
        ##TODO myles
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

    elif server['server_type'] is ServerType.MINECRAFT_JAVA:
        #https://mcstatus.readthedocs.io/en/stable/api/basic/#mcstatus.status_response.JavaStatusPlayer
        #https://mcstatus.readthedocs.io/en/stable/api/basic/#mcstatus.querier.QueryResponse
        pass

    elif server['server_type'] is ServerType.MINECRAFT_BEDROCK:
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
