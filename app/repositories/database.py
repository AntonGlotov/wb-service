from sqlite3 import connect

from app.config.settings import DATABASE_PATH


def connect_db():
    return connect(DATABASE_PATH)
