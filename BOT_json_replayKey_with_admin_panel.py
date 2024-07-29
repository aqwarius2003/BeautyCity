import json
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

from admin import is_admin, show_admin_menu

# Загрузка данных меню из JSON файла
with open('menu.json', 'r', encoding='utf-8') as file:
    menu_data = json.load(file)

users = {}

# Меню больших кнопок
big_keyboard = ["Записаться", "Мои записи", "Салоны", "Мастера", "Администратор"]

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
    telegram_id = update.message.from_user.id
    users[chat_id] = {}
    chat_id = update.message.chat_id
    if is_admin(telegram_id):
        show_admin_menu(update, context)
    else:
    # show_main_menu(update, context, chat_id=chat_id)
        show_big_keyboard(update, context, chat_id)


# Функция для показа больших кнопок
def show_big_keyboard(update: Update, context: CallbackContext, chat_id):
    message = update.message or update.callback_query.message
    if message:
        keyboard = ReplyKeyboardMarkup(
            build_menu(big_keyboard, n_cols=2),
            resize_keyboard=True
        )
        message.reply_text('Выберите опцию:', reply_markup=keyboard)

# Функция отображения основного меню
def show_main_menu(update: Update, context: CallbackContext):
    # Определяем, вызван ли метод из текстового сообщения или callback'а
    if update.message:
        chat_id = update.message.chat_id
        message = update.message
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
        message = update.callback_query.message
    else:
        return

    keyboard = [
        InlineKeyboardButton(menu['name'], callback_data=menu['callback_data']) for menu in menu_data
    ]
    keyboard.append(InlineKeyboardButton("Отказаться", callback_data='decline'))
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 2))
    text = 'Добро пожаловать! Выберите опцию:'
    if users[chat_id]:
        selected_options = '\n'.join([f"{key}: {value}" for key, value in users[chat_id].items()])
        text = f"Вы выбрали:\n{selected_options}\n\n{text}"
    message.reply_text(text, reply_markup=reply_markup)





# Функция отображения меню подтверждения с выбранными опциями
def show_confirmation_menu(update: Update, context: CallbackContext, chat_id, message):
    selected_options = f"Салон: {users[chat_id].get('salons', 'не выбран')}\nУслуга: {users[chat_id].get('services', 'не выбрана')}\nСпециалист: {users[chat_id].get('staffs', 'не выбран')}\nВремя: {users[chat_id].get('time', 'не выбрано')}"
    text = f"Вы выбрали:\n{selected_options}\n\nПодтвердите или измените свой выбор."
    keyboard = [
        InlineKeyboardButton('Подтверждаю', callback_data='confirm'),
        InlineKeyboardButton('Изменить', callback_data='main_menu')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 2))
    message.reply_text(text, reply_markup=reply_markup)

# Функция проверки пользователя в базе данных (заглушка)
def check_user_in_db(user_id):
    return False

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

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    callback_data = query.data
    chat_id = query.message.chat_id

    # Удаляем предыдущее сообщение
    context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)

    if callback_data == 'main_menu':
        show_main_menu(update, context)
        return

    if callback_data == 'confirm':
        if not check_user_in_db(chat_id):
            show_terms(update, context, chat_id, query.message)
        else:
            selected_options = f"Салон: {users[chat_id].get('salons')}\nУслуга: {users[chat_id].get('services')}\nСпециалист: {users[chat_id].get('staffs')}\nВремя: {users[chat_id].get('time')}"
            query.message.reply_text(f"Вы записались на:\n{selected_options}")
        return

    if callback_data == 'agree':
        # Здесь можно добавить логику для сохранения согласия пользователя в базе данных
        selected_options = f"Салон: {users[chat_id].get('salons')}\nУслуга: {users[chat_id].get('services')}\nСпециалист: {users[chat_id].get('staffs')}\nВремя: {users[chat_id].get('time')}"
        query.message.reply_text(f"Вы записались на:\n{selected_options}")
        return

    if callback_data == 'decline':
        users.pop(chat_id, None)
        query.message.reply_text('Вы отказались от записи.')
        show_big_keyboard(update, context, chat_id)
        return

    for menu in menu_data:
        if menu['callback_data'] == callback_data:
            submenus = menu.get('submenu', [])
            keyboard = [
                InlineKeyboardButton(submenu['name'], callback_data=submenu['callback_data']) for submenu in submenus
            ]
            reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 2))
            text = f'Выберите {menu["name"]}:'
            if users[chat_id]:
                selected_options = '\n'.join([f"{key}: {value}" for key, value in users[chat_id].items()])
                text = f"Вы выбрали:\n{selected_options}\n\n{text}"
            query.message.reply_text(text, reply_markup=reply_markup)
            return

        for submenu in menu.get('submenu', []):
            if submenu['callback_data'] == callback_data:
                users[chat_id][menu['callback_data']] = submenu['name']
                if all(key in users[chat_id] for key in ['salons', 'services', 'staffs', 'time']):
                    show_confirmation_menu(update, context, chat_id, query.message)
                else:
                    show_main_menu(update, context)
                return

# Функция отображения сообщения администратора
def show_admin_message(update: Update, context: CallbackContext):
    update.message.reply_text('Мы готовы вас записать в салоны. Позвоните по телефону: +71234567889')
    show_big_keyboard(update, context, update.message.chat_id)

# Функция отображения салонов
def show_salons(update: Update, context: CallbackContext):
    with open('menu.json', 'r', encoding='utf-8') as file:
        menu_data = json.load(file)

    salons = [item for item in menu_data if item['callback_data'] == 'salons']
    message_text = '\n'.join([f"{salon['name']}: {salon.get('description', 'Описание недоступно')}" for salon in salons[0]['submenu']])
    update.message.reply_text(message_text)
    show_big_keyboard(update, context, update.message.chat_id)

# Функция отображения мастеров
def show_staffs(update: Update, context: CallbackContext):
    with open('menu.json', 'r', encoding='utf-8') as file:
        menu_data = json.load(file)

    staffs = [item for item in menu_data if item['callback_data'] == 'staffs']
    message_text = '\n'.join([f"{staff['name']}: {staff.get('description', 'Описание недоступно')}\n" for staff in staffs[0]['submenu']])
    update.message.reply_text(message_text)
    show_big_keyboard(update, context, update.message.chat_id)

# Функция отображения записи пользователя
def show_my_appointments(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    appointments = users.get(chat_id, {})
    if appointments:
        message_text = '\n'.join([f"{key}: {value}" for key, value in appointments.items()])
    else:
        message_text = 'У вас нет записей.'
    update.message.reply_text(message_text)
    show_big_keyboard(update, context, chat_id)

def main():
    # Ваш токен бота
    updater = Updater("6506598877:AAE0D2T8MygorZoF6dxNJmYspSI-lwyKyDo", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text("Записаться"), show_main_menu))
    dp.add_handler(MessageHandler(Filters.text("Мои записи"), show_my_appointments))
    dp.add_handler(MessageHandler(Filters.text("Салоны"), show_salons))
    dp.add_handler(MessageHandler(Filters.text("Мастера"), show_staffs))
    dp.add_handler(MessageHandler(Filters.text("Администратор"), show_admin_message))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
