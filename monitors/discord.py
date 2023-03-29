from logging import getLogger

import requests

from settings import DISCORD_BOT_TOKEN

from .base import Monitor, MonitorException

logger = getLogger(__name__)


class DiscordMonitor(Monitor):
    base_url = "https://discord.com/api/v10"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    guild_id = "812037309376495636"

    def get_channels(self):
        url = f"{self.base_url}/guilds/{self.guild_id}/channels"
        r = requests.get(url, headers=self.headers)
        try:
            r.raise_for_status()
            return r.json()
        except Exception:
            print(r.json())
            raise

    def check_channel_categories_number(self, threshold: int):
        """Checks if the number of channels in each category is close to the limit.

        Args:
            threshold (int): Number of channels in a category that will trigger a warning

        Raises:
            MonitorException: One or more channels are close to the limit
        """

        channels = self.get_channels()
        categories = [x for x in channels if x["type"] == 4]

        message = ""
        for category in categories:
            category_channels = [x for x in channels if x["parent_id"] == category["id"]]
            logger.info("Category %s has %s channels" % (category["name"], len(category_channels)))

            if len(category_channels) >= threshold:
                message += "Category %s has %s channels\r\n\r\n" % (category["name"], len(category_channels))

        if message != "":
            raise MonitorException(message)

    def run(self) -> None:
        # Run all checks
        self.check_channel_categories_number(47)
