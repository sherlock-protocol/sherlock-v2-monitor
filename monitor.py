from logging import getLogger
from time import sleep
from typing import List

import settings
from monitors import ArbRestakeMonitor, DistManagerMonitor, IndexerMonitor, Monitor, Network, ProtocolManagerMonitor
from monitors.base import MonitorException
from telegram import notify_exception, notify_monitor_exception

logger = getLogger(__name__)


class Monitoring:
    monitors: List[Monitor] = []

    def __init__(self):
        logger.info("Setting up monitors")
        self.monitors.append(IndexerMonitor("https://mainnet.indexer.sherlock.xyz", Network.MAINNET))
        self.monitors.append(IndexerMonitor("https://goerli.indexer.sherlock.xyz", Network.GOERLI))
        self.monitors.append(DistManagerMonitor(Network.MAINNET))
        self.monitors.append(DistManagerMonitor(Network.GOERLI))
        self.monitors.append(ProtocolManagerMonitor("https://mainnet.indexer.sherlock.xyz", Network.MAINNET))
        self.monitors.append(ProtocolManagerMonitor("https://goerli.indexer.sherlock.xyz", Network.GOERLI))
        self.monitors.append(ArbRestakeMonitor("https://mainnet.indexer.sherlock.xyz", Network.MAINNET))
        self.monitors.append(ArbRestakeMonitor("https://goerli.indexer.sherlock.xyz", Network.GOERLI))
        logger.info("%s monitors set up.", len(self.monitors))

    def start(self):
        logger.info("Monitor loop started")
        try:
            while True:
                for monitor in self.monitors:
                    monitor_name = f"{monitor.__class__.__name__} - {monitor.network._name_}"
                    try:
                        logger.info("Running %s monitor", monitor_name)
                        monitor.run()
                    except MonitorException as e:
                        logger.error("Monitor %s has failed: %s", monitor_name, e)
                        notify_monitor_exception(monitor_name=monitor_name, exception=e)
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
