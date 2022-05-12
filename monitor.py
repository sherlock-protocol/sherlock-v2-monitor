from time import sleep
from logging import getLogger
from typing import List
from monitors import Monitor, DummyMonitor

import settings

logger = getLogger(__name__)


class Monitoring:
    monitors: List[Monitor] = []

    def __init__(self) -> None:
        logger.debug("Setting up monitors")
        self.monitors.append(DummyMonitor())
        logger.debug("%s monitors set up.", len(self.monitors))

    def start(self):
        logger.info("Monitor loop started")
        try:
            while True:
                for monitor in self.monitors:
                    logger.debug("Running %s monitor", monitor.__class__)
                    monitor.run()

                logger.debug("Sleeping for %ss.", settings.MONITOR_SLEEP_BETWEEN_CALL)
                sleep(settings.MONITOR_SLEEP_BETWEEN_CALL)
        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Monitor loop ended")


def main():
    logger.info("Monitor process started")
    monitor = Monitoring()
    monitor.start()


if __name__ == "__main__":
    main()
