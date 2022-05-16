from enum import Enum
from logging import getLogger

from settings import WEB3_WSS_GOERLI, WEB3_WSS_MAINNET
from utils import requests_retry_session

from .base import Monitor, MonitorException

logger = getLogger(__name__)


class Network(Enum):
    MAINNET = 1
    GOERLI = 5


class IndexerMonitor(Monitor):
    # Indexer URL endpoint
    url: str = None

    # Indexer network
    network: Network = Network.MAINNET

    def __init__(self, url: str, network: Network) -> None:
        self.url = url
        self.network = network

    def get_indexer_status(self):
        """Fetch indexer status"""
        return requests_retry_session().get(f"{self.url}/status").json()["data"]

    def check_indexer_up_to_date(self, last_block: int) -> None:
        """Check if indexer is up to date by comparing it's latest
        processed block with blockchain's block height.

        Args:
            last_block (int): Last processed block number

        Raises:
            MonitorException: Indexer is not up to date
        """
        logger.info("Last processed block is %s", last_block)

        # Fetch blockchain's highest block
        provider = WEB3_WSS_MAINNET if self.network == Network.MAINNET else WEB3_WSS_GOERLI
        highest_block = provider.eth.get_block("latest")["number"]
        logger.info("Highest block is %s", highest_block)

        # Check if indexer is up to date
        delta = highest_block - last_block
        if delta > 20:
            raise MonitorException("Indexer is %s blocks behind" % delta)

    def run(self) -> None:
        # Fetch indexer status
        status = self.get_indexer_status()

        # Run all checks
        self.check_indexer_up_to_date(status["last_block"])
