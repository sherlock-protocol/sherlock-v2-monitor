from logging import getLogger

from database import get_indexer_last_block
from settings import WEB3_WSS

from .base import Monitor, MonitorException

logger = getLogger()


class IndexerMonitor(Monitor):
    def run(self) -> None:
        # Fetch latest block processed by the indexer
        last_block = get_indexer_last_block()
        logger.info("Last processed block is %s", last_block)

        # Fetch blockchain's highest block
        highest_block = WEB3_WSS.eth.get_block("latest")["number"]
        logger.debug("Highest block is %s", highest_block)

        # Check if indexer is up to date
        delta = highest_block - last_block
        if delta > 20:
            raise MonitorException("Indexer is %s blocks behind!" % delta)
