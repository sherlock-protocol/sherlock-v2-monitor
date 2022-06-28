from logging import getLogger

from web3 import Web3
from web3.contract import Contract

from settings import SHERLOCK_DIST_MANAGER_ADDRESS, SHERLOCK_SHER_ABI, SHERLOCK_SHER_ADDRESS, WEB3_GOERLI, WEB3_MAINNET

from .base import Monitor, MonitorException, Network

logger = getLogger(__name__)


class DistManagerMonitor(Monitor):
    # SherToken contract
    sher_contract: Contract = None

    # Web3 provider
    provider: Web3 = None

    def __init__(self, network: Network) -> None:
        super().__init__(network)

        self.provider = WEB3_MAINNET if self.network == Network.MAINNET else WEB3_GOERLI
        self.sher_contract = self.provider.eth.contract(address=SHERLOCK_SHER_ADDRESS, abi=SHERLOCK_SHER_ABI)

    def get_dist_manager_sher_balance(self) -> int:
        """Return DistManager SHER token balance.

        Returns:
            int: SherToken balance of DistManager contract
        """
        return int(
            self.provider.fromWei(self.sher_contract.functions.balanceOf(SHERLOCK_DIST_MANAGER_ADDRESS).call(), "ether")
        )

    def check_if_enough_sher_balance(self, balance: int):
        """Check if DistManager contract has enough SHER tokens.

        Args:
            balance (int): Current SHER tokens balance of DistManager contract

        Raises:
            MonitorException: DistManager contract does not have enough SHER tokens
        """
        logger.info("DistManager has %s SHER tokens.", balance)

        if balance < 1_000_000:
            raise MonitorException("DistManager has only %s SHER tokens" % balance)

    def run(self) -> None:
        balance = self.get_dist_manager_sher_balance()

        # Run all checks
        self.check_if_enough_sher_balance(balance)
