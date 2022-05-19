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
    url = "https://api.telegram.org/bot%s/sendMessage" % settings.TELEGRAM_BOT_TOKEN
    data = {"chat_id": settings.TELEGRAM_CHANNEL, "text": message, "parse_mode": "MarkdownV2"}
    requests_retry_session().post(url, json=data)


def notify_monitor_exception(*, monitor_name: str, exception: MonitorException):
    """Send Telegram message about a failed monitor.

    Args:
        monitor_name (str): Failed monitor's name
        exception (MonitorException): Exception instance
    """

    # We must escape reserved Markdown characters
    message = (
        f"""
    Monitor *{monitor_name}* failed!

    {exception}
    """.replace(
            "!", "\\!"
        )
        .replace("-", "\\-")
        .replace(".", "\\.")
        .replace("|", "\\|")
    )

    # Split message in 4096 characters size chunks
    chunk_size = 4096
    chunks = [message[i : i + chunk_size] for i in range(0, len(message), chunk_size)]

    for chunk in chunks:
        send_telegram_message(message=chunk)


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
