from telegram import KeyboardButton, ReplyKeyboardMarkup

from app.bot.messages import (
    CANCEL_BUTTON_TEXT,
    CHANGE_API_KEY_BUTTON_TEXT,
    RESORT_BUTTON_TEXT,
)


def main_keyboard():
    button_resort = KeyboardButton(RESORT_BUTTON_TEXT)
    button_cancel = KeyboardButton(CANCEL_BUTTON_TEXT)
    button_api = KeyboardButton(CHANGE_API_KEY_BUTTON_TEXT)

    return ReplyKeyboardMarkup(
        [[button_resort, button_cancel, button_api]],
        resize_keyboard=True,
    )
