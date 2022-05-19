from logging import getLogger
from typing import List, TypedDict

from web3 import Web3
from web3.contract import Contract

from settings import SHERLOCK_PROTOCOL_MANAGER_ABI, SHERLOCK_PROTOCOL_MANAGER_ADDRESS, WEB3_WSS_GOERLI, WEB3_WSS_MAINNET
from utils import requests_retry_session

from .base import Monitor, MonitorException, Network

logger = getLogger(__name__)


class Coverage(TypedDict):
    claimable_until: int
    coverage_amount: str
    coverage_amount_set_at: int


class Protocol(TypedDict):
    agent: str
    bytes_identifier: str
    coverage_ended_at: int
    coverages: List[Coverage]
    premium: str
    premium_set_at: str
    tvl: str


class ProtocolManagerMonitor(Monitor):
    protocol_manager_contract: Contract = None

    # Web3 provider
    provider: Web3 = None

    # Indexer URL endpoint
    url: str = None

    def __init__(self, url: str, network: Network) -> None:
        super().__init__(network)

        self.url = url

        self.provider = WEB3_WSS_MAINNET if self.network == Network.MAINNET else WEB3_WSS_GOERLI
        self.protocol_manager_contract = self.provider.eth.contract(
            address=SHERLOCK_PROTOCOL_MANAGER_ADDRESS, abi=SHERLOCK_PROTOCOL_MANAGER_ABI
        )

    def get_protocols(self) -> List[Protocol]:
        """Fetch protocols from indexer.

        Returns:
            List[Protocol]: List of past and present covered protocols
        """
        return requests_retry_session().get(f"{self.url}/protocols").json()["data"]

    def get_protocol_coverage_left(self, id: str) -> int:
        """Fetch protocol's coverage left in seconds.

        Args:
            id (str): Protocol ID

        Returns:
            int: Coverage left in seconds
        """
        return int(self.protocol_manager_contract.functions.secondsOfCoverageLeft(id).call())

    def check_if_enough_balance(self, protocols: List[Protocol]) -> None:
        found_protocols = []

        for protocol in protocols:
            seconds_left = self.get_protocol_coverage_left(protocol["bytes_identifier"])
            days_left = seconds_left / 60 / 60 / 24

            logger.info("Protocol %s has %.1f days of coverage left.", protocol["bytes_identifier"], days_left)

            if days_left < 7:
                found_protocols.append((protocol["bytes_identifier"], days_left))

        if len(found_protocols) > 0:
            message = ""
            for item in found_protocols:
                message += "Protocol *%s* has *%.1f* days of coverage left\r\n\r\n" % (item[0], item[1])

            raise MonitorException(message)

    def run(self) -> None:
        # Fetch protocols
        all_protocols = self.get_protocols()

        # Filter inactive protocols
        active_protocols = [x for x in all_protocols if x["coverage_ended_at"] is None]

        # Run all checks
        self.check_if_enough_balance(active_protocols)
