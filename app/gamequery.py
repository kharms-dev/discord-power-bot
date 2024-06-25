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

logger = logging.getLogger(__name__)
logging.basicConfig(filename='gamequery.log', level=logging.INFO)
logger.setLevel(logging.DEBUG)

def is_anyone_active() -> tuple[bool, list]:
    """
    Checks all known servers for users currently logged in
    returns a tuple of a bool and a list
    """
    try:
        player_count = 0
        if list_servers() == {}:
            load_servers()
        failed_queries = []
        for server in list_servers():
            try:
                server = get_server(server)
                player_count += get_players(server).get('current_players')
            except AttributeError:
                logger.warning("No result, couldn't connect to %s, moving on...", server['name'])
                failed_queries.append(server['name'])
            except Exception:
                traceback.print_exc()
        if player_count > 0:
            return True, failed_queries
        else:
            return False, failed_queries
    except:
        logger.error("Couldn't query servers for active players")
        traceback.print_exc()
        raise


def get_players(server: Server) -> dict:
    """
    Returns a dict with the current number of players connected
    to the server as well as the max players supported
    """
    if server['server_type'] is ServerType.STEAM:
        logger.info("Querying ArmA server: %s", server['name'])
        try:
            steamquery = _steam_server_connection(
                server_ip=str(server['ip_address']), port=server['port'])
            server_state = _lint_steamquery_output(
                steamquery.query_server_info())
            logger.info("%s has %s/%s players active", server['name'], server_state['players'], server_state['max_players'])
            return {"current_players": server_state["players"],
                    "max_players": server_state["max_players"]}
        except ConnectionError:
            logger.error("Could not connect to %s, connection error", server['name'])
        except Exception:
            logger.error("Could not get %s player info", server['name'])
            traceback.print_exc()
            raise

    elif server['server_type'] is ServerType.SPACE_ENGINEERS:
        logger.info("Querying Space Engineers server: %s", server['name'])
        try:
            server_api_address = "http://" + \
                str(server['ip_address']) + ":" + str(server['port'])
            api = VRageAPI(url=server_api_address, token=server['password'])
            server_ping = api.get_server_ping()
            players = api.get_players()
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

            logger.info("%s has %s/%s players active", str(server['name']), player_count, "99")
            return {"current_players": player_count, "max_players": 99}
        except ConnectionError:
            logger.error("Could not connect to %s, connection error", server['name'])
        except Exception:
            logger.error("Could not get %s player info", server['name'])
            traceback.print_exc()
            raise

    elif server['server_type'] is ServerType.MINECRAFT_JAVA:
        logger.info("Querying Minecraft Java server: %s", server['name'])
        try:
            serverinstance = JavaServer(str(server['ip_address']), server['port'])
            status = serverinstance.status()
            logger.info("%s has %s/%s players active", str(server['name']), status.players.online, status.players.max)
            return {"current_players": status.players.online,
                    "max_players": status.players.max}
        except ConnectionError:
            logger.error("Could not connect to %s, connection error", server['name'])
        except Exception:
            logger.error("Could not get %s player info", server['name'])
            traceback.print_exc()
            raise

    elif server['server_type'] is ServerType.MINECRAFT_BEDROCK:
        logger.info("Querying Minecraft Bedrock server: %s", server['name'])
        try:
            serverinstance = BedrockServer(str(server['ip_address']), server['port'])
            status = serverinstance.status()
            logger.info("%s has %s/%s players active", str(server['name']), status.players.online, status.players.max)
            return {"current_players": status.players.online,
                    "max_players": status.players.max}
        except ConnectionError:
            logger.error("Could not connect to %s, connection error", server['name'])
        except Exception:
            logger.error("Could not get %s player info", server['name'])
            traceback.print_exc()
            raise

    elif server['server_type'] is ServerType.DCS:
        logger.info("Querying DCS server: %s", server['name'])
        ##TODO myles
        logger.info("%s has 0/0 players active", server['name'])
        return {"current_players": 0,
                "max_players": 0}

    else:
        logger.error('Cannot query unrecognised server type %s', server_type)


def get_players_details(server: Server) -> list:
    """
    Returns a list with all current player objects containing
    names, scores and durations on the server
    """
    logger.info("Getting player details for %s", server['name'])
    if server['server_type'] is ServerType.STEAM:
        try:
            steamquery = _steam_server_connection(
                server_ip=str(server['ip_address']), port=server['port'])
            player_info = _lint_steamquery_output(
                steamquery.query_player_info())
            return player_info
        except Exception:
            logger.warning("Could not get player info")
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
        logger.error('Cannot query unrecognised server type %s', server_type)

def get_server_details(server: Server) -> list:
    """
    Returns a list with all relevant server config
    """
    logger.info("Getting server details for %s", server['name'])
    if server['server_type'] is ServerType.STEAM:
        try:
            steamquery = _steam_server_connection(
                server_ip=str(server['ip_address']), port=server['port'])
            server_info = _lint_steamquery_output(
                steamquery.query_server_info())
            return server_info

        except Exception:
            logger.warning("Could not get server info for %s", server['name'])
            traceback.print_exc()
            raise
    elif server['server_type'] is ServerType.SPACE_ENGINEERS:
        pass

    elif server['server_type'] is ServerType.DCS:
        pass

    elif server['server_type'] is ServerType.MINECRAFT_JAVA:
        #https://mcstatus.readthedocs.io/en/stable/api/basic/#mcstatus.status_response.JavaStatusPlayer
        #https://mcstatus.readthedocs.io/en/stable/api/basic/#mcstatus.querier.QueryResponse
        try:
            serverinstance = JavaServer(str(server['ip_address']), server['port'])
            query = serverinstance.query()
            print(query)
        except TimeoutError:
            logger.error("Could not query server info for %s, timed out", server['name'])
        except Exception as error:
            logger.error("Could not query server info for %s, %s", server['name'], error)
            traceback.print_exc()
            raise

    elif server['server_type'] is ServerType.MINECRAFT_BEDROCK:
        pass

    else:
        logger.error('Cannot query unrecognised server type %s', server_type)


def _steam_server_connection(server_ip: str, port: int) -> object:
    """
    Creates a steam query server connection object and passes it back.
    """
    logger.info("Connecting to SteamQuery...")
    try:
        # Check if IP address is valid
        if not network.valid_ip_address(server_ip):
            raise ValueError("IP Address Invalid")

        # Check if port is valid
        if not network.valid_port(port):
            raise ValueError("PORT environment variable is invalid")

        # Construct SteamQuery session
        logger.info('Connecting to %s:%s',server_ip , port)
        server = SteamQuery(server_ip, port)
        return server

    except Exception:
        logger.warning("Unable to connect to server")
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
    logger.info("Linting SteamQuery ouput")
    if isinstance(query, list):
        return query
    else:
        try:
            if "error" in query.keys():
                raise ConnectionError(str(query))
            else:
                return query
        except ConnectionError:
            logger.error("Connection error: server may be down")
            raise
        except Exception:
            logger.error("Error passed back from SteamQuery")
            traceback.print_exc()
            raise
