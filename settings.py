import csv
import requests
import json
import os
from logging import Formatter, StreamHandler, getLogger
from logging.handlers import TimedRotatingFileHandler

from decouple import config
from web3 import HTTPProvider, Web3
from web3.middleware import geth_poa_middleware

# EXTERNAL PROTOCOL CSV
PROTOCOL_CSV_ENDPOINT = "https://raw.githubusercontent.com/sherlock-protocol/sherlock-v2-indexer/main/meta/protocols.csv"
resp = requests.get(PROTOCOL_CSV_ENDPOINT)
# id,tag,name,..
# x,x,x,..
# ....
PROTOCOL_CSV = list(csv.reader(resp.text.splitlines()))
# {
#     "0x32132": ["euler", "Euler", ...].
#     "0x32133": ["opyn", "Opyn", ...].
# }
PROTOCOL_METADATA = {}
for entry in PROTOCOL_CSV[1:]:
    PROTOCOL_METADATA[entry[0]] = entry[1:]

# MONITOR
# ------------------------------------------------------------------------------
MONITOR_SLEEP_BETWEEN_CALL = config("MONITOR_SLEEP_BETWEEN_CALL", default=2.0, cast=float)

# WEB3
# ------------------------------------------------------------------------------
WEB3_MAINNET = Web3(HTTPProvider(config("WEB3_PROVIDER_HTTPS_MAINNET"), request_kwargs={"timeout": 180}))
WEB3_GOERLI = Web3(HTTPProvider(config("WEB3_PROVIDER_HTTPS_GOERLI"), request_kwargs={"timeout": 180}))
WEB3_GOERLI.middleware_onion.inject(geth_poa_middleware, layer=0)

# Repo location on system
REPO = config("SHERLOCK_CORE_PATH")

SHERLOCK_SHER_ADDRESS = config("SHERLOCK_SHER_ADDRESS")
with open(os.path.join(REPO, "artifacts", "contracts", "SherToken.sol", "SherToken.json")) as json_data:
    SHERLOCK_SHER_ABI = json.load(json_data)["abi"]

SHERLOCK_DIST_MANAGER_ADDRESS = config("SHERLOCK_DIST_MANAGER_ADDRESS")
SHERLOCK_PROTOCOL_MANAGER_ADDRESS = config("SHERLOCK_PROTOCOL_MANAGER_ADDRESS")
with open(
    os.path.join(
        REPO, "artifacts", "contracts", "managers", "SherlockProtocolManager.sol", "SherlockProtocolManager.json"
    )
) as json_data:
    SHERLOCK_PROTOCOL_MANAGER_ABI = json.load(json_data)["abi"]

# TELEGRAM
# ------------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL = config("TELEGRAM_CHANNEL", cast=int)

# LOGGING
# ------------------------------------------------------------------------------
logger = getLogger()
logger.setLevel("DEBUG")

# Create custom formatter
verbose_formatter = Formatter(
    (
        "[%(asctime)s] %(levelname)-7s "
        "%(module)s %(name)s "
        "{%(filename)s:%(lineno)d} %(process)d %(thread)d - %(message)s"
    )
)


# Redirect INFO+ logs to console and output.log
file_handler = TimedRotatingFileHandler(filename="output.log", when="midnight", utc=True)
file_handler.setLevel("INFO")
file_handler.setFormatter(verbose_formatter)

console_handler = StreamHandler()
console_handler.setLevel("INFO")
console_handler.setFormatter(verbose_formatter)

# Redirect DEBUG+ logs to separate file
debug_file_handler = TimedRotatingFileHandler(filename="debug_output.log", when="midnight", utc=True)
debug_file_handler.setLevel("DEBUG")
debug_file_handler.setFormatter(verbose_formatter)

logger.handlers = []
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(debug_file_handler)
