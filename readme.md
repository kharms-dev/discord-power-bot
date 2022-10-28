# Discord Power Bot

## Usage

* Fill out `.env` file with your Discord token and URLs.

For WOL service, use this Docker image: <https://github.com/daBONDi/go-rest-wol>

For the shutdown, reboot and status URLs, a service that responds to HTTP GETs with code `200` on success is fine, we are using [Airytec SwitchOff](http://www.airytec.com/en/switch-off/).

```sh
docker compose up -d
```

Bare docker cli:

```sh
docker run --env-file=/.env --restart=unless-stopped ghcr.io/mylesagray/discord-power-bot:latest
```
