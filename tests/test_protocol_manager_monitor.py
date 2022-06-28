from unittest import TestCase, mock

from monitors import Network, ProtocolManagerMonitor
from monitors.base import MonitorException


class ProtocolManagerMonitorTests(TestCase):
    def setUp(self) -> None:
        self.monitor = ProtocolManagerMonitor("http://localhost:5000", Network.MAINNET)

    def test_no_error_on_empty_protocols_list(self) -> None:
        self.monitor.check_if_enough_balance([])

    @mock.patch("monitors.protocol_manager.ProtocolManagerMonitor.get_protocol_coverage_left", return_value=100_000_000)
    def test_no_error_on_one_protocol_with_enough_balance(self, *args) -> None:
        self.monitor.check_if_enough_balance([{"bytes_identifier": "0xdeadbeef"}])

    @mock.patch("monitors.protocol_manager.ProtocolManagerMonitor.get_protocol_coverage_left", return_value=999)
    def test_no_error_on_one_protocol_with_low_balance(self, *args) -> None:
        with self.assertRaises(expected_exception=MonitorException):
            self.monitor.check_if_enough_balance([{"bytes_identifier": "0xdeadbeef"}])

    @mock.patch("monitors.protocol_manager.ProtocolManagerMonitor.get_protocol_coverage_left", return_value=100_000_000)
    def test_no_error_on_multiple_protocols_with_enough_balance(self, *args) -> None:
        self.monitor.check_if_enough_balance([{"bytes_identifier": "0xdeadbeef"}, {"bytes_identifier": "0xdeadbeef"}])

    @mock.patch(
        "monitors.protocol_manager.ProtocolManagerMonitor.get_protocol_coverage_left", side_effect=[100_000_000, 999]
    )
    def test_no_error_on_multiple_protocols_and_one_with_low_balance(self, *args) -> None:
        with self.assertRaises(expected_exception=MonitorException):
            self.monitor.check_if_enough_balance(
                [{"bytes_identifier": "0xdeadbeef"}, {"bytes_identifier": "0xdeadbeef"}]
            )
