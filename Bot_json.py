import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, CallbackContext

# Загрузка данных меню из JSON файла
with open('menu.json', 'r', encoding='utf-8') as file:
    menu_data = json.load(file)

users = {}

# Функция для построения меню кнопок
def build_menu(buttons, n_cols):
    return [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]

# Функция для отправки файла соглашения
def send_agreement_document(chat_id, bot):
    document_path = 'soglasie.pdf'
    document = open(document_path, 'rb')
    bot.send_document(chat_id=chat_id, document=document)
    document.close()

# Функция обработки команды /start
def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    users[chat_id] = {}
    show_main_menu(update, context, chat_id, update.message)

# Функция отображения основного меню
def show_main_menu(update: Update, context: CallbackContext, chat_id, message):
    keyboard = [
        InlineKeyboardButton(menu['name'], callback_data=menu['callback_data']) for menu in menu_data
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 1))
    text = 'Добро пожаловать! Выберите опцию:'
    if users[chat_id]:
        selected_options = '\n'.join([f"{key}: {value}" for key, value in users[chat_id].items()])
        text = f"Вы выбрали:\n{selected_options}\n\n{text}"
    message.reply_text(text, reply_markup=reply_markup)

# Функция отображения меню подтверждения с выбранными опциями
def show_confirmation_menu(update: Update, context: CallbackContext, chat_id, message):
    selected_options = f"Салон: {users[chat_id].get('salons', 'не выбран')}\nУслуга: {users[chat_id].get('services', 'не выбрана')}\nСпециалист: {users[chat_id].get('specialists', 'не выбран')}\nВремя: {users[chat_id].get('time', 'не выбрано')}"
    text = f"Вы выбрали:\n{selected_options}\n\nПодтвердите или измените свой выбор."
    keyboard = [
        InlineKeyboardButton('Подтверждаю', callback_data='confirm'),
        InlineKeyboardButton('Изменить', callback_data='main_menu')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 1))
    message.reply_text(text, reply_markup=reply_markup)

# Функция проверки пользователя в базе данных (заглушка)
def check_user_in_db(user_id):
    return True

# Функция отображения условий и кнопок согласия
def show_terms(update: Update, context: CallbackContext, chat_id, message):
    send_agreement_document(chat_id, context.bot)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Согласен", callback_data='agree')],
        [InlineKeyboardButton("Отказаться", callback_data='decline')],
    ])
    message.reply_text(
        'Пожалуйста, подтвердите своё согласие на обработку данных:',
        reply_markup=keyboard
    )

# Функция отображения меню согласия
def show_agreement_menu(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Согласен", callback_data='agree')],
        [InlineKeyboardButton("Отказаться", callback_data='decline')],
    ])
    update.callback_query.message.reply_text(
        'Пожалуйста, подтвердите своё согласие на обработку данных:',
        reply_markup=keyboard
    )

# Функция обработки нажатия кнопок
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    callback_data = query.data
    chat_id = query.message.chat_id

    # Удаляем предыдущее сообщение
    context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)

    if callback_data == 'main_menu':
        show_main_menu(update, context, chat_id, query.message)
        return

    if callback_data == 'confirm':
        if not check_user_in_db(chat_id):
            show_terms(update, context, chat_id, query.message)
        else:
            selected_options = f"Салон: {users[chat_id].get('salons')}\nУслуга: {users[chat_id].get('services')}\nСпециалист: {users[chat_id].get('specialists')}\nВремя: {users[chat_id].get('time')}"
            query.message.reply_text(f"Вы записались на:\n{selected_options}")
        return

    if callback_data == 'agree':
        # Здесь можно добавить логику для сохранения согласия пользователя в базе данных
        selected_options = f"Салон: {users[chat_id].get('salons')}\nУслуга: {users[chat_id].get('services')}\nСпециалист: {users[chat_id].get('specialists')}\nВремя: {users[chat_id].get('time')}"
        query.message.reply_text(f"Вы записались на:\n{selected_options}")
        return

    if callback_data == 'decline':
        query.message.reply_text('Вы отказались от записи.')
        return

    for menu in menu_data:
        if menu['callback_data'] == callback_data:
            submenus = menu.get('submenu', [])
            keyboard = [
                InlineKeyboardButton(submenu['name'], callback_data=submenu['callback_data']) for submenu in submenus
            ]
            reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 1))
            text = f'Выберите {menu["name"]}:'
            if users[chat_id]:
                selected_options = '\n'.join([f"{key}: {value}" for key, value in users[chat_id].items()])
                text = f"Вы выбрали:\n{selected_options}\n\n{text}"
            query.message.reply_text(text, reply_markup=reply_markup)
            return

        for submenu in menu.get('submenu', []):
            if submenu['callback_data'] == callback_data:
                users[chat_id][menu['callback_data']] = submenu['name']
                if all(key in users[chat_id] for key in ['salons', 'services', 'specialists', 'time']):
                    show_confirmation_menu(update, context, chat_id, query.message)
                else:
                    show_main_menu(update, context, chat_id, query.message)
                return

def main():
    # Создаем Updater и передаем ему токен вашего бота.
    updater = Updater("6506598877:AAE0D2T8MygorZoF6dxNJmYspSI-lwyKyDo")

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))

    # Регистрируем обработчик для всех текстовых сообщений
    dp.add_handler(CallbackQueryHandler(button))

    # Запускаем бот
    updater.start_polling()

    # Останавливаем бот при завершении
    updater.idle()

if __name__ == '__main__':
    main()
