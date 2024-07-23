import sqlite3
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

import logging
import os
from dotenv import load_dotenv
# import time
from actions_database import add_client_to_database, is_client_in_database, create_clients_table
from actions_database import download_document

logging.basicConfig()
# logging.getLogger().addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

try:
    load_dotenv()
    TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
    logger.debug("Env variables loaded")
    # logger.debug(f"Work with channel_id {TG_CHANNEL_ID}")
except (KeyError, ValueError):
    logger.critical(
        "Please, set correct env variables: \n"
        "TG_BOT_TOKEN")
    raise


# Функция для обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id
    client_data = is_client_in_database(user_id)

    if client_data:
        first_name = client_data[0]
        update.message.reply_text(f'Добро пожаловать, {user.first_name}!')
        show_main_menu(update)
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Прочитать условия", callback_data='read_terms')],
        ])
        update.message.reply_text(
            f'Здравствуйте, {user.first_name}\nДля регистрации прочитайте условия.',
            reply_markup=keyboard)


# def button(update: Update, context: CallbackContext) -> None:
def button(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == 'agree':
        first_name = query.from_user.first_name
        add_client_to_database(user_id, first_name, phone='')
        query.answer('Спасибо за согласие!')
        query.message.reply_text('Добро пожаловать!')
        show_main_menu(update)
    elif query.data == 'disagree':
        query.answer('Вы отказались от условий использования.')
        query.message.reply_text('К сожалению, мы не можем продолжить без вашего согласия.')
    elif query.data == 'read_terms':
        download_document(query.message.chat_id, context.bot)
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Соглашаюсь", callback_data='agree')],
            [InlineKeyboardButton("Отказываюсь", callback_data='disagree')],
        ])
        query.message.reply_text('Вы прочитали условия. Вы согласны с ними?', reply_markup=keyboard)


def show_main_menu(update: Update) -> None:
    update.message.reply_text('Основное меню будет здесь.')


# Функция для обработки неизвестных команд
def unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Извините, я не понимаю эту команду.')


def main() -> None:
    create_clients_table()
    logger.debug(f"Linked chat id is {TG_BOT_TOKEN}")

    # Создаем экземпляр бота и передаем токен апи
    updater = Updater(TG_BOT_TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Регистрируем обработчик для текстовых сообщений
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    # Регистрируем обработчик неизвестных команд
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("KeyboardInterrupt or exit(), goodbye!")
    except Exception as e:
        logger.exception("Uncaught exception")
