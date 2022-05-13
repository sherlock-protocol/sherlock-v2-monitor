from unittest import TestCase, mock

from monitors import IndexerMonitor
from monitors.base import MonitorException


class IndexerMonitorTests(TestCase):
    def setUp(self) -> None:
        self.monitor = IndexerMonitor()

    @mock.patch("monitors.indexer.WEB3_WSS.eth.get_block", return_value={"number": 42})
    @mock.patch("monitors.indexer.get_indexer_last_block", return_value=42)
    def test_no_error_on_same_block_height(self, mock_1, mock_2) -> None:
        self.monitor.run()

    @mock.patch("monitors.indexer.WEB3_WSS.eth.get_block", return_value={"number": 62})
    @mock.patch("monitors.indexer.get_indexer_last_block", return_value=42)
    def test_no_error_on_small_height_difference(self, mock_1, mock_2) -> None:
        self.monitor.run()

    @mock.patch("monitors.indexer.WEB3_WSS.eth.get_block", return_value={"number": 63})
    @mock.patch("monitors.indexer.get_indexer_last_block", return_value=42)
    def test_raise_exception_on_significant_height_difference(self, mock_1, mock_2) -> None:
        with self.assertRaises(expected_exception=MonitorException):
            self.monitor.run()
