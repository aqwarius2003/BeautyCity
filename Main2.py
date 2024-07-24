# import необходимых модулей
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from handlers import registrate_user_in_db, button_terms, unknown, show_main_menu, start, button_main_menu_handler, \
    back_to_start_handler
from actions_database import create_clients_table
import logging
import os
from dotenv import load_dotenv

# Настройка логгирования
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Загрузка переменных окружения
try:
    load_dotenv()
    TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
    logger.debug("Env variables loaded")
except (KeyError, ValueError):
    logger.critical(
        "Please, set correct env variables: \n"
        "TG_BOT_TOKEN")
    raise


# Основная функция для запуска бота
def main() -> None:
    create_clients_table()
    logger.debug(f"Linked chat id is {TG_BOT_TOKEN}")

    # Создаем экземпляр бота и передаем токен API
    updater = Updater(TG_BOT_TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher
    # Обработчики callback-кнопок
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(back_to_start_handler, pattern='back_to_start'))
    dispatcher.add_handler(CallbackQueryHandler(button_main_menu_handler))


    dispatcher.add_handler(CallbackQueryHandler(button_terms))

    # Регистрируем обработчик для кнопок главного меню


    # Регистрируем обработчик для неизвестных команд
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
