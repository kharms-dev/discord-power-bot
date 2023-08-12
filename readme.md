# Discord Power Bot

## Usage

* Fill out `.env` file with your Discord token and URLs.
* Fill out `servers.json` with your server details and types to allow querying of clients on power requests
* Optional: set `COOLDOWN` for `boot`, `reboot` and `shutdown` cooldown timers in seconds, if left empty it defaults to `300`.
* Optional: set `POWERBOT_ROLE` to limit access to `boot`, `reboot` and `shutdown`. This takes a comma separated list of either role names or role ids, if left unset defaults to the `@everyone` role.

For WOL service, use this Docker image: <https://github.com/daBONDi/go-rest-wol>

For the shutdown, reboot and status URLs, a service that responds to HTTP GETs with code `200` on success is fine, we are using [Airytec SwitchOff](http://www.airytec.com/en/switch-off/).

```sh
docker compose up -d
```

Bare docker cli:

```sh
docker run --env-file=/.env --restart=unless-stopped -v servers.json:/home/appuser/servers.json ghcr.io/mylesagray/discord-power-bot:latest
```
