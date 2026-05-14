import logging
from os import getenv

from dotenv import find_dotenv, load_dotenv, set_key


logger = logging.getLogger(__name__)


def get_wb_api_token():
    load_dotenv()
    return getenv("wb_api_token")


def get_telegram_token():
    load_dotenv()
    return getenv("telegram_token")


def get_telegram_proxy_url():
    load_dotenv()
    return getenv("telegram_proxy_url")


def update_env(key, value):
    dotenv_file = find_dotenv()
    load_dotenv(dotenv_file)
    set_key(dotenv_file, key, value)
    load_dotenv(dotenv_file, override=True)
    logger.info("Environment value updated: key=%s dotenv_file=%s", key, dotenv_file)
