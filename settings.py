from logging import Formatter, StreamHandler, getLogger
from logging.handlers import TimedRotatingFileHandler

from decouple import config

# MONITOR
# ------------------------------------------------------------------------------
MONITOR_SLEEP_BETWEEN_CALL = config("MONITOR_SLEEP_BETWEEN_CALL", default=2.0, cast=float)

# DATABASE
# ------------------------------------------------------------------------------
DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
DB_NAME = config("DB_NAME")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")

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


# Redirect INFO+ logs to console and output.log
file_handler = TimedRotatingFileHandler(filename="output.log", when="midnight", utc=True)
file_handler.setLevel("INFO")
file_handler.setFormatter(verbose_formatter)

console_handler = StreamHandler()
console_handler.setLevel("INFO")
console_handler.setFormatter(verbose_formatter)

# Redirect DEBUG+ logs to separate file
debug_file_handler = TimedRotatingFileHandler(filename="debug_output.log", when="midnight", utc=True)
debug_file_handler.setLevel("DEBUG")
debug_file_handler.setFormatter(verbose_formatter)

logger.handlers = []
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(debug_file_handler)
