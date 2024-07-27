# admin_menu.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
import json
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Идентификаторы администраторов
ADMIN_IDS = [309093652]  # Пример ID администратора


# Функция проверки является ли пользователь администратором
def is_admin(telegram_id):
    return telegram_id in ADMIN_IDS


# Функция для загрузки меню администратора из JSON
def load_admin_menu(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        admin_menu = json.load(file)
    return admin_menu


# Функция для отображения меню администратора
def show_admin_menu(update: Update, context: CallbackContext):
    logger.info("Отображение меню администратора")

    admin_menu = load_admin_menu('admin_menu.json')

    options = []
    for item in admin_menu:
        options.append(item['name'])

    # Разбиваем кнопки на два столбца
    options_chunked = [options[i:i + 2] for i in range(0, len(options), 2)]

    reply_markup = ReplyKeyboardMarkup(options_chunked, resize_keyboard=True)
    update.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    context.user_data['admin_menu'] = admin_menu  # Сохраняем меню в user_data для дальнейшего использования
    context.user_data['current_menu'] = 'main'


# Функция для отображения подменю
def show_submenu(update, context, submenu):
    options = [item['name'] for item in submenu]

    # Добавляем кнопку "Назад", если ее еще нет
    if "Назад" not in options:
        options.append("Назад")

    # Разбиваем кнопки на два столбца
    options_chunked = [options[i:i + 2] for i in range(0, len(options), 2)]

    reply_markup = ReplyKeyboardMarkup(options_chunked, resize_keyboard=True)
    update.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    context.user_data['current_menu'] = 'submenu'
    context.user_data['submenu'] = submenu


# Обработчик для выбора в меню администратора
def handle_admin_choice(update: Update, context: CallbackContext):
    user_choice = update.message.text
    current_menu = context.user_data.get('current_menu', 'main')
    admin_menu = context.user_data.get('admin_menu', [])

    if user_choice == "Назад" and current_menu == 'submenu':
        show_admin_menu(update, context)
        return

    if current_menu == 'main':
        for item in admin_menu:
            if item['name'] == user_choice:
                if 'submenu' in item:
                    show_submenu(update, context, item['submenu'])
                else:
                    update.message.reply_text(f'Вы выбрали: {user_choice}')
                return
    elif current_menu == 'submenu':
        submenu = context.user_data.get('submenu', [])
        for submenu_item in submenu:
            if submenu_item['name'] == user_choice:
                update.message.reply_text(f'Вы выбрали: {submenu_item["name"]}')
                return

    update.message.reply_text('Неверный выбор. Пожалуйста, попробуйте еще раз.')
