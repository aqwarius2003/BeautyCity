from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import json

# Загрузка данных из JSON
with open('menu.json', 'r', encoding='utf-8') as file:
    menu_data = json.load(file)


# Функция обработки команды /start
def start(update, context):
    # Создание основного меню с кнопками категорий в два столбца
    main_menu_keyboard = []
    for category in menu_data:
        category_name = category['name']
        main_menu_keyboard.append([InlineKeyboardButton(category_name, callback_data=f"menu_{category_name.lower()}")])

    reply_markup = InlineKeyboardMarkup(main_menu_keyboard)
    update.message.reply_text('Выберите категорию:', reply_markup=reply_markup)


# Функция обработки выбора пункта меню
def menu_callback(update, context):
    query = update.callback_query
    query.answer()

    # Получаем название выбранной категории из callback_data
    category_name = query.data.split('_')[1]

    # Находим выбранное меню по названию категории
    chosen_category = next((item for item in menu_data if item['name'].lower() == category_name), None)

    if chosen_category:
        if category_name.lower() == 'салоны':
            # Показываем подменю салонов
            submenu_keyboard = []
            for salon in chosen_category['submenu']:
                submenu_keyboard.append([InlineKeyboardButton(salon['name'], callback_data=salon['callback_data'])])

            reply_markup = InlineKeyboardMarkup(submenu_keyboard)
            query.edit_message_text(text='Выберите салон красоты:', reply_markup=reply_markup)

        else:
            # В случае других категорий можно дополнить логику здесь
            query.edit_message_text(text="Эта функция временно недоступна.")

    else:
        query.edit_message_text(text="Что-то пошло не так, попробуйте еще раз.")


# Функция обработки выбора конкретного салона
def salon_callback(update, context):
    query = update.callback_query
    query.answer()

    salon_name = query.data

    chosen_salon = None
    for category in menu_data:
        if category['name'].lower() == 'салоны':
            chosen_salon = next((salon for salon in category['submenu'] if salon['callback_data'] == salon_name), None)
            break

    if chosen_salon:
        description = chosen_salon['description']
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('Записаться', callback_data=f"book_{salon_name}")],
            [InlineKeyboardButton('Назад', callback_data='back_to_salons')]
        ])
        query.edit_message_text(text=f"{description}\n\nВыберите действие:", reply_markup=reply_markup)
    else:
        query.edit_message_text(text="Информация о салоне не найдена.")


# Функция обработки нажатия кнопки "Назад" при просмотре салонов
def back_to_salons_callback(update, context):
    query = update.callback_query
    query.answer()

    start(update, context)  # Возвращаемся к списку салонов


# Функция обработки нажатия кнопок "Записаться" или "Назад" при просмотре салонов
def salon_action_callback(update, context):
    query = update.callback_query
    query.answer()

    action = query.data.split('_')[0]  # Определяем тип действия (book или back_to_salons)

    if action == 'book':
        query.edit_message_text(text="Функция бронирования временно недоступна.")
    elif action == 'back':
        start(update, context)  # Возвращаемся к списку салонов


# Функция обработки неизвестных команд
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, такая команда не поддерживается.")


def main():
    # Токен вашего бота
    updater = Updater('6506598877:AAE0D2T8MygorZoF6dxNJmYspSI-lwyKyDo', use_context=True)

    # Регистрация обработчиков
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(menu_callback, pattern='^menu_'))
    updater.dispatcher.add_handler(CallbackQueryHandler(salon_callback, pattern='^salon\d+$'))
    updater.dispatcher.add_handler(CallbackQueryHandler(salon_action_callback, pattern='^(book|back)_'))
    updater.dispatcher.add_handler(CallbackQueryHandler(back_to_salons_callback, pattern='^back_to_salons$'))

    updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Запуск бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
