# Sherlock V2 Health Monitor
![GitHub](https://img.shields.io/github/license/sherlock-protocol/sherlock-v2-monitor)

Smart contracts and indexer health monitoring tool.

## Monitors

| Name | Description |
| --- | --- |
| IndexerMonitor | Checks if the indexer is up to date with the latest blocks. |

## Installation

Requirements:
 - **python** version `>=3.8.6`

```bash
$ git clone https://github.com/sherlock-protocol/sherlock-v2-monitor.git
$ cd sherlock-v2-monitor

# Set up environment variables
$ cp .env.example .env

# Install dependencies
$ pip install -r requirements.txt

# Run monitor
$ python monitor.py
```

### Telegram Integration
There are two environment variables necessary for sending notifications to a Telegram channel.

##### TELEGRAM_BOT_TOKEN
Telegram bot authentication token. See [Telegram docs](https://core.telegram.org/bots/api#authorizing-your-bot)

#### TELEGRAM_CHANNEL
Telegram Channel ID. There are various ways for getting the ID of a channel, but the easiest one is to forward a message, from that channel, to [Json Dump Bot](https://telegram.me/JsonDumpBot).

### License

This project is licensed under the [MIT License.](./LICENSE)
