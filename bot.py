from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from os import getenv
from functions import sort_tasks, resort_tasks, delete_supp, update_tasks, fetch_id, patch_supply, create_supply, clear_supplies, authorization, update_env, check_connect
from sqlite3 import connect
from excel_parcing import export_to_sqlite
import asyncio
from requests import get

load_dotenv()
API_TOKEN = getenv('telegram_token')

cancel_flag = False  # Глобальная переменная для отмены


async def start(update: Update, context):
    button_resort = KeyboardButton('Пересортировать')
    button_cancel = KeyboardButton('Отменить')
    button_api = KeyboardButton('Поменять ключ API')

    keyboard = ReplyKeyboardMarkup([[button_resort, button_cancel, button_api]], resize_keyboard=True)

    await update.message.reply_text(
        "Нажмите на кнопку ниже, чтобы запустить программу.",
        reply_markup=keyboard
    )


async def button_pressed(update: Update, context):
    global cancel_flag

    if update.message.text == 'Пересортировать':
        cancel_flag = False  # Сбрасываем флаг отмены перед началом задачи
        await update.message.reply_text("Запуск пересортировки")
        task = asyncio.create_task(run_resort_tasks(update, context))  # Асинхронный запуск задачи

    elif update.message.text == 'Отменить':
        cancel_flag = True  # Устанавливаем флаг отмены
        await update.message.reply_text("Отмена задачи")

    elif update.message.text == 'Поменять ключ API':
        await update.message.reply_text('Отправьте новый API ключ')
        context.user_data['waiting_for_api_key'] = True  # Ставим флаг

    elif context.user_data.get('waiting_for_api_key'):
        new_api_key = update.message.text
        update_env('wb_api_token', new_api_key)

        if check_connect():
            await update.message.reply_text('✅ Ключ обновлён!')
            context.user_data.pop('waiting_for_api_key')  # Убираем флаг
        else:
            await update.message.reply_text('❌ Неверный API ключ. Попробуйте ещё раз:')



async def run_resort_tasks(update: Update, context):
    await asyncio.sleep(5)  # 5 секунд на подумать
    global cancel_flag

    if get('https://common-api.wildberries.ru/ping', headers=authorization()).status_code == 401:
        await update.message.reply_text("Закончился срок действия API токена")
        cancel_flag = True

    if cancel_flag:
        await update.message.reply_text("Отмена")
        return

    await update.message.reply_text("Начата пересортировка...")

    update_tasks()
    clear_supplies()

    con = connect('database.sqlite3')
    cur = con.cursor()
    cur.execute('SELECT article, supply_name FROM art_supp')

    for x in cur.fetchall():
        if cancel_flag:
            await update.message.reply_text("Отмена")
            con.commit()
            con.close()
            return
        a = fetch_id(x[0])

        if len(a) == 0:
            continue

        patch_supply(create_supply(x[1]), a)
    con.commit()
    con.close()
    await update.message.reply_text("Сортировка завершена")


async def handle_file(update: Update, context):
    file = update.message.document

    if file.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':  # Проверка, что это Excel файл
        file_path = await file.get_file()  # Получаем путь к файлу на серверах Telegram
        file_name = file.file_name

        # Скачиваем файл во временную директорию
        file_path = await file_path.download_to_drive(
            custom_path=f'./uploads/Articules.xlsx')
        print(file_path)

        try:
            export_to_sqlite(file_path)  # Передаем файл в функцию
            await update.message.reply_text("Файл успешно обработан")
        except Exception as e:
            await update.message.reply_text(f"Ошибка при обработке файла: {str(e)}")
        # finally:
        # os.remove(file_name)  # Удаляем файл после обработки
    else:
        await update.message.reply_text("Пожалуйста, отправьте корректный Excel файл.")


def main():
    app = ApplicationBuilder().token(API_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_pressed))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))  # Добавляем обработку файлов

    app.run_polling()


if __name__ == '__main__':
    main()