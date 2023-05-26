from datetime import datetime, timedelta
from logging import getLogger
from typing import List, TypedDict

from utils import requests_retry_session

from .base import Monitor, MonitorException, Network

logger = getLogger(__name__)


class StakingPosition(TypedDict):
    id: int
    usdc: str
    lockup_end: int


class ArbRestakeMonitor(Monitor):
    # Indexer URL endpoint
    url: str = None

    def __init__(self, url: str, network: Network) -> None:
        super().__init__(network)
        self.url = url

    def get_indexer_status(self):
        """Fetch indexer status"""
        return requests_retry_session().get(f"{self.url}/status").json()["data"]

    def check_arb_positions(self, positions: List[StakingPosition]) -> None:
        """Check if there are any staking positions that can be arb-restaked.

        Args:
            positions (List[StakingPosition]): List of active staking positions

        Raises:
            MonitorException: At least a position can be arb-restaked.
        """
        now = datetime.now()

        # We store position IDs in a list
        found_positions = []

        for position in positions:
            lockup_end = datetime.fromtimestamp(position["lockup_end"])
            balance = int(position["usdc"]) / 1e6

            # Positions can be arb-restaked after 2 weeks after their lockup ends
            arb_period_start = lockup_end + timedelta(days=14)
            days_until_arb = (arb_period_start - now).days

            # Skip positions less than 2 USDC (which won't be restaked)
            if balance < 2:
                continue

            if days_until_arb < 7:
                found_positions.append((position["id"], days_until_arb, balance))

        # Sort by time left
        found_positions = sorted(found_positions, key=lambda x: x[1])

        if len(found_positions) > 0:
            message = "Found the following staking positions that can be arb-restaked\r\n\r\n"
            message += "   ID     | Time left until arb-restake | USDC\r\n"
            message += "------------------------------------------------------------\r\n"
            for item in found_positions:
                message += "{:^9s} {:>10s} days {:>20,} USDC\r\n".format(str(item[0]), str(item[1]), item[2])
            raise MonitorException(message)

    def run(self) -> None:
        # Fetch indexer status
        try:
            status = self.get_indexer_status()
        except Exception as e:
            logger.exception(e)
            raise MonitorException("Failed to fetch indexer status")

        # Run all checks
        self.check_arb_positions(status["staking_positions"])
