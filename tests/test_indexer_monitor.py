from unittest import TestCase, mock

from monitors import IndexerMonitor
from monitors.base import MonitorException
from monitors.indexer import Network


@mock.patch("monitors.indexer.IndexerMonitor.get_indexer_status", return_value={"last_block": 42})
class IndexerMonitorTests(TestCase):
    def setUp(self) -> None:
        self.monitor = IndexerMonitor("http://localhost", Network.MAINNET)

    @mock.patch("monitors.indexer.WEB3_WSS_MAINNET.eth.get_block", return_value={"number": 42})
    def test_no_error_on_same_block_height(self, *args) -> None:
        self.monitor.run()

    @mock.patch("monitors.indexer.WEB3_WSS_MAINNET.eth.get_block", return_value={"number": 62})
    def test_no_error_on_small_height_difference(self, *args) -> None:
        self.monitor.run()

    @mock.patch("monitors.indexer.WEB3_WSS_MAINNET.eth.get_block", return_value={"number": 63})
    def test_raise_exception_on_significant_height_difference(self, *args) -> None:
        with self.assertRaises(expected_exception=MonitorException):
            self.monitor.run()
