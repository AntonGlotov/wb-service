import asyncio
import logging

from telegram import Update

from app.bot.keyboards import main_keyboard
from app.bot.messages import (
    API_KEY_INVALID_TEXT,
    API_KEY_UPDATED_TEXT,
    CANCEL_BUTTON_TEXT,
    CANCEL_TASK_TEXT,
    CANCEL_TEXT,
    CHANGE_API_KEY_BUTTON_TEXT,
    FILE_PROCESSED_TEXT,
    FILE_PROCESSING_ERROR_TEXT,
    INVALID_EXCEL_FILE_TEXT,
    RESORT_BUTTON_TEXT,
    RESORT_FINISHED_TEXT,
    RESORT_IN_PROGRESS_TEXT,
    RESORT_STARTED_TEXT,
    SEND_API_KEY_TEXT,
    START_TEXT,
    TOKEN_EXPIRED_TEXT,
    WB_API_ERROR_TEXT,
)
from app.config.settings import ARTICLE_FILE_PATH
from app.clients.wildberries_client import WildberriesAPIError, check_connect, is_token_expired
from app.config.env import update_env
from app.services.excel_import_service import export_to_sqlite
from app.services.article_supply_service import list_article_supplies
from app.services.orders_service import update_tasks
from app.services.sorting_service import (
    process_article_supply,
)
from app.services.supplies_service import clear_supplies


logger = logging.getLogger(__name__)
cancel_flag = False


def _user_id(update: Update):
    return update.effective_user.id if update.effective_user else None


async def start(update: Update, context):
    logger.info("Start command received: user_id=%s", _user_id(update))
    await update.message.reply_text(START_TEXT, reply_markup=main_keyboard())


async def button_pressed(update: Update, context):
    global cancel_flag

    if update.message.text == RESORT_BUTTON_TEXT:
        logger.info("Resort requested: user_id=%s", _user_id(update))
        cancel_flag = False
        await update.message.reply_text(RESORT_STARTED_TEXT)
        asyncio.create_task(run_resort_tasks(update, context))

    elif update.message.text == CANCEL_BUTTON_TEXT:
        logger.info("Resort cancellation requested: user_id=%s", _user_id(update))
        cancel_flag = True
        await update.message.reply_text(CANCEL_TASK_TEXT)

    elif update.message.text == CHANGE_API_KEY_BUTTON_TEXT:
        logger.info("API key change requested: user_id=%s", _user_id(update))
        await update.message.reply_text(SEND_API_KEY_TEXT)
        context.user_data["waiting_for_api_key"] = True

    elif context.user_data.get("waiting_for_api_key"):
        logger.info("New Wildberries API key received: user_id=%s", _user_id(update))
        new_api_key = update.message.text
        update_env("wb_api_token", new_api_key)

        if check_connect():
            logger.info("New Wildberries API key accepted: user_id=%s", _user_id(update))
            await update.message.reply_text(API_KEY_UPDATED_TEXT)
            context.user_data.pop("waiting_for_api_key")
        else:
            logger.warning("New Wildberries API key rejected: user_id=%s", _user_id(update))
            await update.message.reply_text(API_KEY_INVALID_TEXT)


async def run_resort_tasks(update: Update, context):
    await asyncio.sleep(5)
    global cancel_flag

    try:
        logger.info("Resort task started: user_id=%s", _user_id(update))
        if is_token_expired():
            logger.warning("Resort task stopped because Wildberries token expired: user_id=%s", _user_id(update))
            await update.message.reply_text(TOKEN_EXPIRED_TEXT)
            cancel_flag = True

        if cancel_flag:
            logger.info("Resort task cancelled before processing: user_id=%s", _user_id(update))
            await update.message.reply_text(CANCEL_TEXT)
            return

        await update.message.reply_text(RESORT_IN_PROGRESS_TEXT)

        update_tasks()
        clear_supplies()
        article_supplies = list_article_supplies()
        logger.info("Resort task loaded article supplies: count=%s", len(article_supplies))
        processed_count = 0
        skipped_count = 0

        for article, supply_name in article_supplies:
            if cancel_flag:
                logger.info(
                    "Resort task cancelled during processing: user_id=%s processed=%s skipped=%s",
                    _user_id(update),
                    processed_count,
                    skipped_count,
                )
                await update.message.reply_text(CANCEL_TEXT)
                return

            if process_article_supply(article, supply_name):
                processed_count += 1
            else:
                skipped_count += 1
    except WildberriesAPIError as e:
        logger.exception("Resort task failed with Wildberries API error: user_id=%s", _user_id(update))
        await update.message.reply_text(WB_API_ERROR_TEXT.format(error=str(e)))
        return
    except Exception:
        logger.exception("Resort task failed with unexpected error: user_id=%s", _user_id(update))
        raise

    logger.info(
        "Resort task finished: user_id=%s processed=%s skipped=%s",
        _user_id(update),
        processed_count,
        skipped_count,
    )
    await update.message.reply_text(RESORT_FINISHED_TEXT)


async def handle_file(update: Update, context):
    file = update.message.document
    logger.info(
        "Document received: user_id=%s file_name=%r mime_type=%r file_size=%s",
        _user_id(update),
        file.file_name,
        file.mime_type,
        file.file_size,
    )

    if file.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        file_path = await file.get_file()
        file_path = await file_path.download_to_drive(custom_path=ARTICLE_FILE_PATH)
        logger.info("Document downloaded: user_id=%s path=%s", _user_id(update), file_path)

        try:
            export_to_sqlite(file_path)
            logger.info("Document processed successfully: user_id=%s path=%s", _user_id(update), file_path)
            await update.message.reply_text(FILE_PROCESSED_TEXT)
        except Exception as e:
            logger.exception("Document processing failed: user_id=%s path=%s", _user_id(update), file_path)
            await update.message.reply_text(FILE_PROCESSING_ERROR_TEXT.format(error=str(e)))
    else:
        logger.warning(
            "Document rejected due to invalid mime type: user_id=%s mime_type=%r",
            _user_id(update),
            file.mime_type,
        )
        await update.message.reply_text(INVALID_EXCEL_FILE_TEXT)
