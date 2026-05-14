import logging

from telegram.error import NetworkError, TimedOut


logger = logging.getLogger(__name__)


async def handle_error(update, context):
    error = context.error

    if isinstance(error, (NetworkError, TimedOut)):
        logger.warning("Telegram network error: %s", error)
        return

    logger.exception("Unhandled Telegram error", exc_info=error)
