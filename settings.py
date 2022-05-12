from decouple import config
from logging import getLogger, Formatter, StreamHandler
from logging.handlers import TimedRotatingFileHandler

MONITOR_SLEEP_BETWEEN_CALL = config(
    "MONITOR_SLEEP_BETWEEN_CALL", default=2.0, cast=float
)

# LOGGING
# ------------------------------------------------------------------------------
logger = getLogger()
logger.setLevel("DEBUG")

# Create custom formatter
verbose_formatter = Formatter(
    (
        "[%(asctime)s] %(levelname)-7s "
        "%(module)s %(name)s "
        "{%(filename)s:%(lineno)d} %(process)d %(thread)d - %(message)s"
    )
)


# Redirect all logs to console and output.log
file_handler = TimedRotatingFileHandler(
    filename="output.log", when="midnight", utc=True
)
file_handler.setLevel("DEBUG")
file_handler.setFormatter(verbose_formatter)

console_handler = StreamHandler()
console_handler.setLevel("DEBUG")
console_handler.setFormatter(verbose_formatter)

logger.handlers = []
logger.addHandler(console_handler)
logger.addHandler(file_handler)
