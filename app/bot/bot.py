import logging

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest

from app.bot.error_handlers import handle_error
from app.bot.handlers import button_pressed, handle_file, start
from app.config.env import get_telegram_proxy_url, get_telegram_token
from app.config.logging_config import setup_logging


REQUEST_TIMEOUT = 30
logger = logging.getLogger(__name__)


def build_app():
    request_kwargs = {
        "connect_timeout": REQUEST_TIMEOUT,
        "read_timeout": REQUEST_TIMEOUT,
        "write_timeout": REQUEST_TIMEOUT,
        "pool_timeout": REQUEST_TIMEOUT,
    }
    proxy_url = get_telegram_proxy_url()
    if proxy_url:
        request_kwargs["proxy_url"] = proxy_url
        logger.info("Telegram proxy configured")
    else:
        logger.info("Telegram proxy is not configured")

    app = (
        ApplicationBuilder()
        .token(get_telegram_token())
        .request(HTTPXRequest(**request_kwargs))
        .get_updates_request(HTTPXRequest(**request_kwargs))
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_pressed))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_error_handler(handle_error)
    logger.info("Telegram application built and handlers registered")

    return app


def main():
    setup_logging()
    logger.info("Starting Telegram bot polling")
    build_app().run_polling(
        bootstrap_retries=-1,
        poll_interval=1,
        timeout=20,
    )


if __name__ == "__main__":
    main()
