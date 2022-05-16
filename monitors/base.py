from abc import ABC, abstractmethod
from enum import Enum


class Network(Enum):
    MAINNET = 1
    GOERLI = 5


class Monitor(ABC):
    """Base class for any function that is meant to monitor anything."""

    # Indexer network
    network: Network = Network.MAINNET

    @abstractmethod
    def run(self) -> None:
        """Function which executes this monitor's checks.

        Should raise an exception with a custom message if the check fails."""

        pass


class MonitorException(Exception):
    """Custom Exception class."""

    pass
