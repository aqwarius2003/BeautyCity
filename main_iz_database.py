import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, CallbackContext
from database import get_customer_by_telegram_id, get_upcoming_appointments, get_available_salons, get_available_services, get_available_staff, create_appointment, delete_appointment
from datetime import datetime
import os
import django

# Установите переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty.settings')  # Замените 'your_project_name' на имя вашего проекта

# Запуск Django
django.setup()

from database import get_customer_by_telegram_id, get_upcoming_appointments, get_available_salons, get_available_services, get_available_staff, create_appointment, delete_appointment


# Загрузка токена из файла .env
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

users = {}

def build_menu(buttons, n_cols):
    return [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]

def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user = update.message.from_user
    telegram_id = user.id
    first_name = user.first_name

    # Поиск или создание пользователя
    customer = get_customer_by_telegram_id(telegram_id)
    if not customer:
        # Создать нового пользователя
        customer = Customer(first_name=first_name, telegram_id=telegram_id)
        customer.save()

    # Проверка на наличие предстоящих записей
    upcoming_appointments = get_upcoming_appointments(customer)
    if upcoming_appointments:
        appointment = upcoming_appointments[0]
        appointment_info = (
            f"Вы уже записаны на услугу {appointment.get_services()} "
            f"в салон {appointment.salon.name} к специалисту {appointment.staff.first_name} {appointment.staff.last_name} "
            f"на {appointment.date_time.strftime('%d.%m.%Y %H:%M')}"
        )
        keyboard = [
            [InlineKeyboardButton("Удалить запись", callback_data=f'delete_{appointment.id}'),
             InlineKeyboardButton("Изменить", callback_data='change'),
             InlineKeyboardButton("Подтвердить", callback_data='confirm')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(appointment_info, reply_markup=reply_markup)
    else:
        users[chat_id] = {}
        show_main_menu(update, context, chat_id, update.message)

def show_main_menu(update: Update, context: CallbackContext, chat_id, message):
    keyboard = [
        InlineKeyboardButton("Салоны", callback_data='choose_salon'),
        InlineKeyboardButton("Услуги", callback_data='choose_service'),
        InlineKeyboardButton("Специалисты", callback_data='choose_staff'),
        InlineKeyboardButton("Время и дата", callback_data='choose_datetime')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 2))
    text = 'Добро пожаловать! Выберите опцию:'
    if users.get(chat_id):
        selected_options = ', '.join([f"{key}: {value}" for key, value in users[chat_id].items()])
        text = f"Вы выбрали {selected_options}\n\n{text}"
    message.reply_text(text, reply_markup=reply_markup)

def show_confirmation_menu(update: Update, context: CallbackContext, chat_id, message):
    selected_options = (
        f"Салон: {users[chat_id].get('salon', 'не выбран')}\n"
        f"Специалист: {users[chat_id].get('staff', 'не выбран')}\n"
        f"Услуга: {users[chat_id].get('service', 'не выбрана')}\n"
        f"Дата и время: {users[chat_id].get('datetime', 'не выбрано')}"
    )
    text = f"Вы выбрали:\n{selected_options}\n\nПодтвердите или измените свой выбор."
    keyboard = [
        InlineKeyboardButton('Подтверждаю', callback_data='confirm'),
        InlineKeyboardButton('Изменить', callback_data='main_menu')
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 2))
    message.reply_text(text, reply_markup=reply_markup)

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
        customer = get_customer_by_telegram_id(query.from_user.id)
        salon = Salon.objects.get(name=users[chat_id]['salon'])
        service = Service.objects.get(name=users[chat_id]['service'])
        staff = Staff.objects.get(first_name=users[chat_id]['staff'].split()[0], last_name=users[chat_id]['staff'].split()[1])
        date_time = datetime.strptime(users[chat_id]['datetime'], '%d.%m.%Y %H:%M')
        create_appointment(customer, service, staff, salon, date_time)
        query.message.reply_text(f"Вы успешно записались на услугу {service.name} в салон {salon.name} к специалисту {staff.first_name} {staff.last_name} на {date_time}.")
        return

    if callback_data == 'change':
        show_main_menu(update, context, chat_id, query.message)
        return

    if callback_data.startswith('delete_'):
        appointment_id = int(callback_data.split('_')[1])
        delete_appointment(appointment_id)
        query.message.reply_text("Запись удалена.")
        return

    if callback_data.startswith('choose_'):
        chosen_option = callback_data.split('_')[1]
        if chosen_option == 'salon':
            salons = get_available_salons()
            keyboard = [
                [InlineKeyboardButton(salon.name, callback_data=f'salon_{salon.id}') for salon in salons]
            ]
            reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 2))
            query.message.reply_text("Выберите салон:", reply_markup=reply_markup)
        elif chosen_option == 'service':
            services = get_available_services()
            keyboard = [
                [InlineKeyboardButton(service.name, callback_data=f'service_{service.id}') for service in services]
            ]
            reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 2))
            query.message.reply_text("Выберите услугу:", reply_markup=reply_markup)
        elif chosen_option == 'staff':
            selected_salon = Salon.objects.get(name=users[chat_id]['salon'])
            selected_service = Service.objects.get(name=users[chat_id]['service'])
            staff = get_available_staff(salon=selected_salon, service=selected_service)
            keyboard = [
                [InlineKeyboardButton(f"{staff_member.first_name} {staff_member.last_name}", callback_data=f'staff_{staff_member.id}') for staff_member in staff]
            ]
            reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 2))
            query.message.reply_text("Выберите специалиста:", reply_markup=reply_markup)
        elif chosen_option == 'datetime':
            # Здесь должна быть логика выбора времени и даты.
            # Это может быть реализовано через отдельное меню или inline календарь.
            # Например, можно вывести доступные слоты.
            pass

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
