import csv
from logging import getLogger
from typing import List, TypedDict

import requests
from web3 import Web3
from web3.contract import Contract

from settings import SHERLOCK_PROTOCOL_MANAGER_ABI, SHERLOCK_PROTOCOL_MANAGER_ADDRESS, WEB3_GOERLI, WEB3_MAINNET
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

        self.provider = WEB3_MAINNET if self.network == Network.MAINNET else WEB3_GOERLI
        self.protocol_manager_contract = self.provider.eth.contract(
            address=SHERLOCK_PROTOCOL_MANAGER_ADDRESS, abi=SHERLOCK_PROTOCOL_MANAGER_ABI
        )

    def get_protocol_metadata(self) -> dict:
        # TODO: Update the Protocol class to include these fields and add this to the `get_protocols` function

        # EXTERNAL PROTOCOL CSV
        PROTOCOL_CSV_ENDPOINT = (
            "https://raw.githubusercontent.com/sherlock-protocol/sherlock-v2-indexer/main/meta/protocols.csv"
        )
        resp = requests.get(PROTOCOL_CSV_ENDPOINT)
        # id,tag,name,..
        # x,x,x,..
        # ....
        PROTOCOL_CSV = list(csv.reader(resp.text.splitlines()))
        # {
        #     "0x32132": ["euler", "Euler", ...].
        #     "0x32133": ["opyn", "Opyn", ...].
        # }

        return {entry[0]: entry[1:] for entry in PROTOCOL_CSV[1:]}

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

    def get_protocol_balance_left(self, id: str) -> int:
        """Fetch protocol's balance left in USDC with 6 decimals.

        Args:
            id (str): Protocol ID

        Returns:
            int: Protocol balance left in USDC with 6 decimals
        """
        return int(self.protocol_manager_contract.functions.activeBalance(id).call())

    def check_if_enough_balance(self, protocols: List[Protocol]) -> None:
        protocol_metadata = self.get_protocol_metadata()
        found_protocols = []

        for protocol in protocols:
            seconds_left = self.get_protocol_coverage_left(protocol["bytes_identifier"])
            days_left = seconds_left / 60 / 60 / 24

            logger.info("Protocol %s has %.1f days of coverage left.", protocol["bytes_identifier"], days_left)

            if days_left <= 10:
                found_protocols.append(("days", protocol["bytes_identifier"], days_left))

            balance_left = self.get_protocol_balance_left(protocol["bytes_identifier"])
            balance_left = balance_left / 10**6

            logger.info("Protocol %s has %.2f USDC balance left.", protocol["bytes_identifier"], balance_left)

            if balance_left < 750:
                found_protocols.append(("min", protocol["bytes_identifier"], balance_left))

        if len(found_protocols) > 0:
            message = ""
            for item in found_protocols:
                if item[0] == "days":
                    message += "Protocol *%s* has *%.1f* days of coverage left\r\n\r\n" % (
                        protocol_metadata[item[1]][1],
                        item[2],
                    )
                elif item[0] == "min":
                    message += "Protocol *%s* has only *%.2f* USDC balance left\r\n\r\n" % (
                        protocol_metadata[item[1]][1],
                        item[2],
                    )

            raise MonitorException(message)

    def run(self) -> None:
        # Fetch protocols
        try:
            all_protocols = self.get_protocols()
        except Exception as e:
            logger.exception(e)
            raise MonitorException("Failed to fetch protocols from indexer")

        # Filter inactive protocols
        active_protocols = [x for x in all_protocols if x["coverage_ended_at"] is None]

        # Run all checks
        self.check_if_enough_balance(active_protocols)
