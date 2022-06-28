from unittest import TestCase, mock

from monitors import IndexerMonitor
from monitors.base import MonitorException
from monitors.indexer import Network


class IndexerMonitorTests(TestCase):
    def setUp(self) -> None:
        self.monitor = IndexerMonitor("http://localhost", Network.MAINNET)

    @mock.patch("monitors.indexer.WEB3_MAINNET.eth.get_block", return_value={"number": 42})
    def test_no_error_on_same_block_height(self, *args) -> None:
        self.monitor.check_indexer_up_to_date(42)

    @mock.patch("monitors.indexer.WEB3_MAINNET.eth.get_block", return_value={"number": 52})
    def test_no_error_on_small_height_difference(self, *args) -> None:
        self.monitor.check_indexer_up_to_date(42)

    @mock.patch("monitors.indexer.WEB3_MAINNET.eth.get_block", return_value={"number": 53})
    def test_raise_exception_on_significant_height_difference(self, *args) -> None:
        with self.assertRaises(expected_exception=MonitorException):
            self.monitor.check_indexer_up_to_date(42)

    def test_no_error_on_normal_apy(self) -> None:
        self.monitor.check_indexer_apy(4.5)
        self.monitor.check_indexer_apy(1)
        self.monitor.check_indexer_apy(15)

    def test_raise_exception_on_negative_apy(self) -> None:
        with self.assertRaises(expected_exception=MonitorException):
            self.monitor.check_indexer_apy(-4.5)

    def test_raise_exception_on_zero_apy(self) -> None:
        with self.assertRaises(expected_exception=MonitorException):
            self.monitor.check_indexer_apy(0)

    def test_raise_exception_on_high_apy(self) -> None:
        with self.assertRaises(expected_exception=MonitorException):
            self.monitor.check_indexer_apy(25)
