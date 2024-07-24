from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from actions_database import add_client_to_database, is_client_in_database, download_document
from messages import super_start, terms_read_message, welcome_back_message, admin_message
from keyboard import button_main_menu

# Функция для регистрации пользователя в базе данных
def registrate_user_in_db(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id
    client_data = is_client_in_database(user_id)

    if client_data:
        first_name = client_data[0]
        update.message.reply_text(text=welcome_back_message)
        show_main_menu(update)
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Прочитать условия", callback_data='read_terms')],
        ])
        update.message.reply_text(
            f'Здравствуйте, {user.first_name}\nДля регистрации прочитайте условия.',
            reply_markup=keyboard)

# Функция для обработки нажатий кнопок
def button_terms(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == 'agree':
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        first_name = query.from_user.first_name
        add_client_to_database(user_id, first_name, phone='')
        query.answer('Спасибо за согласие!')
        update.callback_query.message.reply_text('Добро пожаловать!')
        show_main_menu(update)

    elif query.data == 'disagree':
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        query.answer('Вы отказались от условий использования.')
        update.callback_query.message.reply_text('К сожалению, мы не можем продолжить без вашего согласия.')

    elif query.data == 'read_terms':
        download_document(query.message.chat_id, context.bot)
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Соглашаюсь", callback_data='agree'),
             InlineKeyboardButton("Отказываюсь", callback_data='disagree')],
        ])

        # Проверяем, что есть доступ к update.callback_query.message
        if update.callback_query.message:
            update.callback_query.message.reply_text(text=terms_read_message, reply_markup=keyboard)

# Функция для отображения основного меню
def show_main_menu(update: Update) -> None:
    update.message.reply_text(text=welcome_back_message)

# Функция для обработки неизвестных команд
def unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Извините, я не понимаю эту команду.')

# Функция для обработки команды /start
# def start(update: Update, context: CallbackContext) -> None:
#     user = update.message.from_user
#     user_id = user.id
 # Выводим приветственное сообщение
    # update.message.reply_text(super_start)

    # Отправляем пользователю меню с инлайн кнопками
    # keyboard = build_main_menu_keyboard()
    # update.message.reply_text(super_start, reply_markup=keyboard)

def start(update: Update, context: CallbackContext, chat_id=None) -> None:
    user = update.effective_user  # Получаем пользователя
    user_id = user.id
 # Отправляем пользователю меню с инлайн кнопками
    keyboard = build_main_menu_keyboard()
    if chat_id is not None:
        context.bot.send_message(chat_id=chat_id, text=super_start, reply_markup=keyboard)
    else:
        update.message.reply_text(super_start, reply_markup=keyboard)


# Функция для построения клавиатуры главного меню
def build_main_menu_keyboard():
    keyboard = []
    buttons = list(button_main_menu.items())

    # Проходим по кнопкам парами
    for i in range(0, len(buttons), 2):
        button1 = InlineKeyboardButton(buttons[i][1], callback_data=buttons[i][0])
        if i + 1 < len(buttons):
            button2 = InlineKeyboardButton(buttons[i + 1][1], callback_data=buttons[i + 1][0])
            keyboard.append([button1, button2])
        else:
            keyboard.append([button1])

    return InlineKeyboardMarkup(keyboard)

# Обработчик для кнопок главного меню
def button_main_menu_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    print(query)

    # Получаем данные, связанные с кнопкой
    button_data = query.data
    print(button_data)
    # Обрабатываем нажатие кнопки
    if button_data == 'salon':
        # Действие для опции 1
        query.edit_message_text(text="Вы выбрали опцию salon")
    elif button_data == 'masters':
        # Действие для опции 2
        query.edit_message_text(text="Вы выбрали опцию masters")
    elif button_data == 'services':
        # Действие для опции 3
        query.edit_message_text(text="Вы выбрали опцию services")
    elif button_data == "administrator":
        # Показываем сообщение из модуля messages.py
        query.edit_message_text(text=admin_message, reply_markup=back_to_start_keyboard())
        # query.edit_message_text(text="Вы выбрали опцию administrator")
    else:
        # В случае неизвестной кнопки (на всякий случай)
        query.edit_message_text(text="Вы выбрали неизвестную опцию")

# Функция для клавиатуры "Назад" с возвратом на /start
def back_to_start_keyboard():

    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='back_to_start')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчик для кнопки "Назад"
def back_to_start_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    # Показываем начальный экран снова
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    start(update, context, chat_id=query.message.chat_id)

