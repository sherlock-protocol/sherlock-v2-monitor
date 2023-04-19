from logging import getLogger

from settings import WEB3_GOERLI, WEB3_MAINNET
from utils import requests_retry_session

from .base import Monitor, MonitorException, Network

logger = getLogger(__name__)


class IndexerMonitor(Monitor):
    # Indexer URL endpoint
    url: str = None

    def __init__(self, url: str, network: Network) -> None:
        super().__init__(network)
        self.url = url

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
        provider = WEB3_MAINNET if self.network == Network.MAINNET else WEB3_GOERLI
        highest_block = provider.eth.get_block("latest")["number"]
        logger.info("Highest block is %s", highest_block)

        # Check if indexer is up to date
        delta = highest_block - last_block
        if delta > 10:
            raise MonitorException("Indexer is %s blocks behind" % delta)

    def check_indexer_apy(self, apy: float):
        """Check if APY is in normal parameters.

        Args:
            apy (float): APY value as percentage
        """
        logger.info("APY is %s", apy)

        if apy < 0:
            raise MonitorException("APY is negative! (%s)" % apy)

        if apy == 0:
            raise MonitorException("There is no APY!")

        if apy > 0.25:
            raise MonitorException("APY is abnormaly high! (%s)" % apy)

    def run(self) -> None:
        # Fetch indexer status
        try:
            status = self.get_indexer_status()
        except Exception as e:
            logger.exception(e)
            raise MonitorException("Failed to fetch indexer status")

        # Run all checks
        self.check_indexer_up_to_date(status["last_block"])
        self.check_indexer_apy(status["apy"])
