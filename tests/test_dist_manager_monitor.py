from unittest import TestCase

from monitors import DistManagerMonitor
from monitors.base import MonitorException
from monitors.indexer import Network


class DistManagerMonitorTests(TestCase):
    def setUp(self) -> None:
        self.monitor = DistManagerMonitor(Network.MAINNET)

    def test_no_error_on_normal_sher_balance(self) -> None:
        self.monitor.check_if_enough_sher_balance(3_000_000)
        self.monitor.check_if_enough_sher_balance(1_000_000)
        self.monitor.check_if_enough_sher_balance(100_000_000)

    def test_raise_exception_on_empty_balance(self) -> None:
        with self.assertRaises(expected_exception=MonitorException):
            self.monitor.check_if_enough_sher_balance(0)

    def test_raise_exception_on_low_balance(self) -> None:
        with self.assertRaises(expected_exception=MonitorException):
            self.monitor.check_if_enough_sher_balance(999_999)
