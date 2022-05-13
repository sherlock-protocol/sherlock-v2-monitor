import settings
from monitors.base import MonitorException
from utils import requests_retry_session


def send_telegram_message(*, message: str):
    """Send a Telegram message.

    Note: As the message allows for Markdown formatting, the message body must be correctly escaped,
    or the message will not be sent.

    Args:
        message (str): Message body.
    """
    r = requests_retry_session()
    url = "https://api.telegram.org/bot%s/sendMessage" % settings.TELEGRAM_BOT_TOKEN
    data = {"chat_id": settings.TELEGRAM_CHANNEL, "text": message, "parse_mode": "MarkdownV2"}
    r.post(url, json=data)


def notify_monitor_exception(*, monitor_name: str, exception: MonitorException):
    """Send Telegram message about a failed monitor.

    Args:
        monitor_name (str): Failed monitor's name
        exception (MonitorException): Exception instance
    """

    message = f"""
    Monitor *{monitor_name}* failed!

    {exception}
    """.replace(
        "!", "\\!"  # We escape ! characters since they are reserved in Markdown
    )

    send_telegram_message(message=message)


def notify_exception(*, exception: Exception):
    """Send Telegram message about an encountered exception.

    Args:
        exception (Exception): Exception instance
    """
    message = f"""
    Encountered exception:

    {exception}
    """

    send_telegram_message(message=message)
