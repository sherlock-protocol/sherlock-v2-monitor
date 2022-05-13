from abc import ABC, abstractmethod


class Monitor(ABC):
    """Base class for any function that is meant to monitor anything."""

    @abstractmethod
    def run(self) -> None:
        """Function which executes this monitor's checks.

        Should raise an exception with a custom message if the check fails."""

        pass


class MonitorException(Exception):
    """Custom Exception class."""

    pass
