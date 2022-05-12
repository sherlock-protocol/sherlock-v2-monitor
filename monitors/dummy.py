from .base import Monitor

from logging import getLogger

logger = getLogger()


class DummyMonitor(Monitor):
    def run(self) -> None:
        logger.info("This is just a dummy monitor. Everything is ok.")
