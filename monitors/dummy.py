from logging import getLogger

from .base import Monitor

logger = getLogger()


class DummyMonitor(Monitor):
    def run(self) -> None:
        logger.info("This is just a dummy monitor. Everything is ok.")
