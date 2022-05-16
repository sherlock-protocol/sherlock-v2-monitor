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

    def get_protocol_balance(self, id: str) -> int:
        """Fetch protocol's active balance.

        Args:
            id (str): Protocol ID

        Returns:
            int: Active balance in USDC
        """
        return int(self.protocol_manager_contract.functions.activeBalance(id).call() / 10**6)

    def check_if_enough_balance(self, protocols: List[Protocol]) -> None:
        for protocol in protocols:
            balance = self.get_protocol_balance(protocol["bytes_identifier"])
            logger.info("Protocol %s active balance is %s USDC", protocol["bytes_identifier"], balance)

            if balance < 1_000:
                raise MonitorException(
                    "Protocol %s has an active balance of only %s USDC" % (protocol["bytes_identifier"], balance)
                )

    def run(self) -> None:
        # Fetch protocols
        all_protocols = self.get_protocols()

        # Filter inactive protocols
        active_protocols = [x for x in all_protocols if x["coverage_ended_at"] is None]

        # Run all checks
        self.check_if_enough_balance(active_protocols)
