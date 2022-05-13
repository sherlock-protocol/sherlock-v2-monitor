from logging import getLogger
from time import sleep
from typing import List

import settings
from monitors import DummyMonitor, IndexerMonitor, Monitor

logger = getLogger(__name__)


class Monitoring:
    monitors: List[Monitor] = []

    def __init__(self):
        logger.debug("Setting up monitors")
        self.monitors.append(DummyMonitor())
        self.monitors.append(IndexerMonitor())
        logger.debug("%s monitors set up.", len(self.monitors))

    def start(self):
        logger.info("Monitor loop started")
        try:
            while True:
                for monitor in self.monitors:
                    try:
                        logger.debug("Running %s monitor", monitor.__class__.__name__)
                        monitor.run()
                    except Exception as e:
                        logger.exception(e)

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
