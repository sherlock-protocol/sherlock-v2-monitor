from logging import getLogger

from database import get_indexer_last_block

from .base import Monitor

logger = getLogger()


class IndexerMonitor(Monitor):
    def run(self) -> None:
        last_block = get_indexer_last_block()
        logger.info("Last processed block is %s", last_block)
