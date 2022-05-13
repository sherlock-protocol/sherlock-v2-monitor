import contextlib
from logging import getLogger

import psycopg2

import settings

logger = getLogger(__name__)


@contextlib.contextmanager
def indexer_db_connection():
    logger.debug("Creating indexer DB connection")
    connection = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASS,
        dbname=settings.DB_NAME,
    )
    cursor = connection.cursor()

    yield cursor

    logger.debug("Closing indexer DB connection")
    cursor.close()
    connection.close()


def get_indexer_last_block():
    with indexer_db_connection() as db:
        db.execute("SELECT last_block FROM INDEXER_STATE;")
        last_block = db.fetchone()[0]

        return last_block
