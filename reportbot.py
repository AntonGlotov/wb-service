from os import getenv
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from datetime import datetime, timedelta
from dailyreport import make_report, update_db

load_dotenv()
BOT_TOKEN = getenv('telegram_report_token')


async def start(update: Update, context):
    # Создаем клавиатуру с одной кнопкой
    keyboard = [[(datetime.now() - timedelta(days=2)).strftime("%d.%m.%Y"),
                 (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y"),
                 datetime.now().strftime("%d.%m.%Y"),],
                # [InlineKeyboardButton("Неделя", callback_data='5')],
                ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Нажмите на кнопку для получения отчета:",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context):
    await update.message.reply_text('Сейчас посмотрю')
    update_db()
    report = make_report(update.message.text.split('-'))
    await update.message.reply_text(f'{update.message.text}\n{report}')


def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()