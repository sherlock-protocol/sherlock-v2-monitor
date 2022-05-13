from unittest import TestCase, mock

import telegram
from monitors.base import MonitorException


class TelegramTests(TestCase):
    @mock.patch("telegram.send_telegram_message")
    def test_send_telegram_message_on_exception(self, mock_send_telegram_message):
        telegram.notify_exception(exception=Exception("test"))
        self.assertEqual(mock_send_telegram_message.call_count, 1)

    @mock.patch("telegram.send_telegram_message")
    def test_send_telegram_message_on_monitor_exception(self, mock_send_telegram_message):
        telegram.notify_monitor_exception(monitor_name="Test monitor", exception=MonitorException("test"))
        self.assertEqual(mock_send_telegram_message.call_count, 1)

    @mock.patch("telegram.requests_retry_session")
    def test_call_telegram_api_on_message_send(self, mock_requests):
        telegram.send_telegram_message(message="Test message")
        self.assertEqual(mock_requests.call_count, 1)
