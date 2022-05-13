from logging import getLogger
from time import sleep
from typing import List

import settings
from monitors import DummyMonitor, IndexerMonitor, Monitor
from monitors.base import MonitorException
from telegram import notify_exception, notify_monitor_exception

logger = getLogger(__name__)


class Monitoring:
    monitors: List[Monitor] = []

    def __init__(self):
        logger.info("Setting up monitors")
        self.monitors.append(DummyMonitor())
        self.monitors.append(IndexerMonitor())
        logger.info("%s monitors set up.", len(self.monitors))

    def start(self):
        logger.info("Monitor loop started")
        try:
            while True:
                for monitor in self.monitors:
                    try:
                        logger.info("Running %s monitor", monitor.__class__.__name__)
                        monitor.run()
                    except MonitorException as e:
                        logger.error("Monitor %s has failed: %s", monitor.__class__.__name__, e)
                        notify_monitor_exception(monitor_name=monitor.__class__.__name__, exception=e)
                    except Exception as e:
                        logger.exception(e)
                        notify_exception(exception=e)

                logger.info("Sleeping for %ss.", settings.MONITOR_SLEEP_BETWEEN_CALL)
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
