import os

import psycopg


def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if database_url is None:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    return database_url


def get_connection():
    return psycopg.connect(get_database_url())
