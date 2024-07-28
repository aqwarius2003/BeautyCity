from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty.settings')
django.setup()

from property.models import Customer, Service, Staff, Salon, Schedule, Appointment
from datetime import datetime, timedelta, timezone

from admin import is_admin, show_admin_menu

users = {}

# Меню больших кнопок
big_keyboard = ["Записаться", "Мои записи", "Салоны", "Мастера", "Услуги", "Администратор"]

def build_keyboard_two_columns(buttons):
    keyboard = []
    row = []
    for i in range(len(buttons)):
        if hasattr(buttons[i], 'name'):
            button_text = buttons[i].name
        else:
            button_text = f"{buttons[i].first_name} {buttons[i].last_name}"
        row.append(InlineKeyboardButton(button_text, callback_data=f'{buttons[i].__class__.__name__.lower()}_{buttons[i].id}'))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


# Функция для отправки файла соглашения
def send_agreement_document(chat_id, bot):
    document_path = 'soglasie.pdf'  # замените на ваш путь к файлу
    document = open(document_path, 'rb')
    bot.send_document(chat_id=chat_id, document=document)
    document.close()


# Функция обработки команды /start
def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    telegram_id = update.message.from_user.id
    users[chat_id] = {}
    if is_admin(telegram_id):
        show_admin_menu(update, context)
    else:
        show_big_keyboard(update, context, chat_id)


# Функция для показа больших кнопок
def show_big_keyboard(update: Update, context: CallbackContext, chat_id):
    message = update.message or update.callback_query.message
    if message:
        keyboard = ReplyKeyboardMarkup(
            [big_keyboard[i:i + 2] for i in range(0, len(big_keyboard), 2)],
            resize_keyboard=True
        )
        message.reply_text('Выберите опцию:', reply_markup=keyboard)


# Функция отображения основного меню
def show_main_menu(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_data = context.user_data

    # Инициализация user_data для нового пользователя
    if chat_id not in users:
        users[chat_id] = {}
        user_data.clear()

    # Получаем имя пользователя из базы данных или используем имя из Telegram
    try:
        customer = Customer.objects.get(telegram_id=chat_id)
        user_name = f"{customer.first_name} {customer.last_name}"
    except Customer.DoesNotExist:
        user_name = update.effective_user.first_name or "Иван Иванов"

    # Формируем текст с информацией о выбранных параметрах
    booking_info = f"{user_name}, вы хотите записаться:\n"
    booking_info += f"Салон: {'выберите в меню' if 'salon_id' not in user_data else Salon.objects.get(id=user_data['salon_id']).name}\n"
    booking_info += f"Услуга: {'выберите в меню' if 'service_id' not in user_data else Service.objects.get(id=user_data['service_id']).name}\n"
    if 'staff_id' in user_data:
        booking_info += f"Мастер: {Staff.objects.get(id=user_data['staff_id']).first_name} {Staff.objects.get(id=user_data['staff_id']).last_name}\n"
    else:
        booking_info += f"Мастер: выберите в меню\n"
    booking_info += f"Дата: {'выберите в меню' if 'date' not in user_data else user_data['date']}\n"
    booking_info += f"Время: {'выберите в меню' if 'time' not in user_data else user_data['time']}\n"

    # Проверяем, заполнены ли все поля
    if 'salon_id' in user_data and 'service_id' in user_data and 'staff_id' in user_data and 'date' in user_data and 'time' in user_data:
        show_confirmation(update, context)
    else:
        keyboard = [
            [InlineKeyboardButton("Выбрать салон", callback_data='select_salon'),
            InlineKeyboardButton("Выбрать услугу", callback_data='select_service')],
            [InlineKeyboardButton("Выбрать мастера", callback_data='select_staff'),
            InlineKeyboardButton("Выбрать дату", callback_data='select_date')],
            [InlineKeyboardButton("Выбрать время", callback_data='select_time')],
            [InlineKeyboardButton("Отменить запись", callback_data='cancel_booking')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.effective_message.reply_text(booking_info, reply_markup=reply_markup)




def show_salons_menu(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    service_id = context.user_data.get('service_id')
    staff_id = context.user_data.get('staff_id')
    date = context.user_data.get('date')

    filters = {}
    if service_id:
        filters['schedules__staff__services__id'] = service_id
    if staff_id:
        filters['schedules__staff_id'] = staff_id
    if date:
        filters['schedules__date'] = date

    salons = Salon.objects.filter(**filters).distinct()

    keyboard = build_keyboard_two_columns(salons)
    keyboard.inline_keyboard.append([InlineKeyboardButton("Назад", callback_data='main_menu')])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите салон", reply_markup=keyboard)


def show_services_menu(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    salon_id = context.user_data.get('salon_id')
    staff_id = context.user_data.get('staff_id')
    date = context.user_data.get('date')

    filters = {}
    if salon_id:
        filters['staff__schedules__salon_id'] = salon_id
    if staff_id:
        filters['staff__id'] = staff_id
    if date:
        filters['staff__schedules__date'] = date

    services = Service.objects.filter(**filters).distinct()

    keyboard = build_keyboard_two_columns(services)
    keyboard.inline_keyboard.append([InlineKeyboardButton("Назад", callback_data='main_menu')])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите услугу", reply_markup=keyboard)

def show_staff_menu(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    salon_id = context.user_data.get('salon_id')
    service_id = context.user_data.get('service_id')
    if salon_id and service_id:
        staffs = Staff.objects.filter(services__id=service_id, schedules__salon_id=salon_id).distinct()
    elif service_id:
        staffs = Staff.objects.filter(services__id=service_id).distinct()
    else:
        staffs = Staff.objects.all()
    keyboard = build_keyboard_two_columns(staffs).inline_keyboard
    keyboard.append([InlineKeyboardButton("Назад", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text("Выберите мастера:", reply_markup=reply_markup)


def show_date_picker(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    staff_id = context.user_data.get('staff_id')
    if staff_id:
        available_dates = Schedule.objects.filter(staff_id=staff_id).values_list('date', flat=True).distinct()
    else:
        available_dates = Schedule.objects.all().values_list('date', flat=True).distinct()
    keyboard = [
        [InlineKeyboardButton(date.strftime("%d.%m.%Y"), callback_data=f'date_{date.strftime("%Y-%m-%d")}')]
        for date in available_dates
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text("Выберите дату:", reply_markup=reply_markup)


def show_time_picker(update: Update, context: CallbackContext):
    user_data = context.user_data
    staff_id = user_data.get('staff_id')
    date_str = user_data.get('date')
    if staff_id and date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        staff = Staff.objects.get(id=staff_id)
        available_times = staff.get_available_time(Service.objects.get(id=user_data['service_id']), date)
        keyboard = [
            [InlineKeyboardButton(time.strftime("%H:%M"), callback_data=f'time_{time.strftime("%H:%M")}')] for time in available_times
        ]
        if not available_times:
            update.effective_message.reply_text("К сожалению, на выбранную дату и время нет доступных записей.")
        else:
            keyboard.append([InlineKeyboardButton("Назад", callback_data='main_menu')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.effective_message.reply_text("Выберите время:", reply_markup=reply_markup)
    else:
        update.effective_message.reply_text("Сначала выберите дату и мастера.")
        show_main_menu(update, context)


def show_confirmation(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_data = context.user_data
    salon = Salon.objects.get(id=user_data['salon_id'])
    service = Service.objects.get(id=user_data['service_id'])
    staff = Staff.objects.get(id=user_data['staff_id'])

    confirmation_text = f"Подтвердите запись:\n" \
                        f"Салон: {salon.name}\n" \
                        f"Услуга: {service.name}\n" \
                        f"Мастер: {staff.first_name} {staff.last_name}\n" \
                        f"Дата: {user_data['date']}\n" \
                        f"Время: {user_data['time']}"

    keyboard = [
        [InlineKeyboardButton("Подтвердить", callback_data='confirm')],
        [InlineKeyboardButton("Отменить", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(confirmation_text, reply_markup=reply_markup)


def save_appointment_from_user_data(update, context):
    user_data = context.user_data
    chat_id = update.effective_chat.id
    if 'salon_id' in user_data and 'service_id' in user_data and 'staff_id' in user_data and 'date' in user_data and 'time' in user_data:
        try:
            customer = Customer.objects.get(telegram_id=chat_id)
            salon = Salon.objects.get(id=user_data['salon_id'])
            service = Service.objects.get(id=user_data['service_id'])
            staff = Staff.objects.get(id=user_data['staff_id'])
            date = user_data['date']
            time = user_data['time']

            appointment = Appointment(
                customer=customer,
                salon=salon,
                staff=staff,
                date=date,
                start_time=time,
                service=service
            )
            appointment.save()
            context.bot.send_message(chat_id=chat_id, text="Запись успешно создана!")
        except Customer.DoesNotExist:
            context.bot.send_message(chat_id=chat_id,
                                     text="Ошибка при создании записи. Пожалуйста, попробуйте снова.")
        except Exception as e:
            context.bot.send_message(chat_id=chat_id,
                                     text=f"Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.")
            print(e)
    else:
        context.bot.send_message(chat_id=chat_id, text="Не хватает данных для создания записи.")

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    callback_data = query.data
    chat_id = query.message.chat_id
    user_data = context.user_data

    if callback_data.startswith('salon_'):
        salon_id = int(callback_data.split('_')[1])
        user_data['salon_id'] = salon_id
        show_main_menu(update, context)  # Возвращаемся к главному меню после выбора
    elif callback_data.startswith('service_'):
        service_id = int(callback_data.split('_')[1])
        user_data['service_id'] = service_id
        show_main_menu(update, context)  # Возвращаемся к главному меню после выбора
    elif callback_data.startswith('staff_'):
        staff_id = int(callback_data.split('_')[1])
        user_data['staff_id'] = staff_id
        show_main_menu(update, context)  # Возвращаемся к главному меню после выбора
    elif callback_data.startswith('date_'):
        date = callback_data.split('_')[1]
        user_data['date'] = date
        show_main_menu(update, context)  # Возвращаемся к главному меню после выбора
    elif callback_data == 'select_time':
        show_time_picker(update, context)  # Вызываем функцию выбора времени
    elif callback_data.startswith('time_'):
        time = callback_data.split('_')[1]
        user_data['time'] = time
        show_main_menu(update, context)  # Возвращаемся к главному меню после выбора
    elif callback_data == 'confirm':
        save_appointment_from_user_data(update, context)
        user_data.clear()
        # show_main_menu(update, context)
    #     handle_confirmation(update, context)
    elif callback_data == 'confirm_cancel':
        handle_confirm_cancel(update, context)
    elif callback_data == 'cancel':
        user_data.clear()
        show_main_menu(update, context)
    elif callback_data == 'agree':
        request_phone_number(update, context, chat_id)
    elif callback_data == 'decline':
        users.pop(chat_id, None)
        query.message.reply_text('Вы отказались от записи.')
        show_big_keyboard(update, context, chat_id)
    elif callback_data == 'select_salon':
        show_salons_menu(update, context)
    elif callback_data == 'select_service':
        show_services_menu(update, context)
    elif callback_data == 'select_staff':
        show_staff_menu(update, context)
    elif callback_data == 'select_date':
        show_date_picker(update, context)
    elif callback_data == 'main_menu':
        show_main_menu(update, context)
    elif callback_data == 'cancel_booking':
        handle_cancel_booking(update, context)


# Функция обработки отмены записи
def handle_cancel_booking(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    user_data = context.user_data
    if user_data:
        keyboard = [
            [InlineKeyboardButton("Да", callback_data='confirm_cancel'),
            InlineKeyboardButton("Нет", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text("Вы уверены, что хотите отменить запись?", reply_markup=reply_markup)
    else:
        query.message.reply_text("У вас нет активной записи.")
        show_main_menu(update, context)

def handle_confirm_cancel(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    user_data = context.user_data
    user_data.clear()
    show_main_menu(update, context)


# Функция отображения условий и кнопок согласия
def show_terms(update: Update, context: CallbackContext, chat_id: object):
    send_agreement_document(chat_id, context.bot)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Согласен", callback_data='agree')],
        [InlineKeyboardButton("Отказаться", callback_data='decline')],
    ])
    update.effective_message.reply_text(
        'Пожалуйста, подтвердите своё согласие на обработку данных:',
        reply_markup=keyboard
    )


# Функция для показа записей пользователя
def show_my_appointments(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    try:
        customer = Customer.objects.get(telegram_id=chat_id)
        appointments = Appointment.objects.filter(customer=customer)
        if appointments.exists():
            for appointment in appointments:
                message_text = f"Салон: {appointment.salon.name}\n"
                message_text += f"Мастер: {appointment.staff.first_name} {appointment.staff.last_name}\n"
                # message_text += f"Услуга: {', '.join([s.name for s in appointment.services.all()])}\n"
                message_text += f"Услуга: {appointment.service.name}\n"
                message_text += f"Дата: {appointment.date}\n"
                message_text += f"Время: {appointment.start_time}\n\n"
                keyboard = [
                    [InlineKeyboardButton("Изменить", callback_data=f'edit_appointment_{appointment.id}')],
                    [InlineKeyboardButton("Подтвердить", callback_data=f'confirm_appointment_{appointment.id}')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(message_text, reply_markup=reply_markup)
        else:
            update.message.reply_text("У вас нет текущих записей.")
    except Customer.DoesNotExist:
        update.message.reply_text("Вы еще не зарегистрированы у нас")
        show_terms(update, context, chat_id)


def show_admin_message(update: Update, context: CallbackContext):
    update.message.reply_text('Мы готовы вас записать в салоны. Позвоните по телефону: +71234567889')
    show_big_keyboard(update, context, update.message.chat_id)


def show_salons(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    salons = Salon.objects.all()

    if salons.exists():
        message_text = "Доступные салоны:\n"
        for salon in salons:
            message_text += f"{salon.name} - {salon.address}\n"
    else:
        message_text = "Салоны не найдены."

    update.message.reply_text(message_text)


def show_staffs(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    staffs = Staff.objects.all()

    if staffs.exists():
        message_text = "Доступные мастера:\n"
        for staff in staffs:
            message_text += f"{staff.first_name} {staff.last_name}\n"
            message_text += f"Специализация: {staff.get_services()}\n"
            message_text += f"Описание: {staff.description}\n\n"
    else:
        message_text = "Мастера не найдены."

    update.message.reply_text(message_text)


def show_services(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    services = Service.objects.all()

    if services.exists():
        message_text = "Доступные услуги:\n"
        for service in services:
            message_text += f"{service.name} - {service.description} - {service.price} руб.\n"
    else:
        message_text = "Услуги не найдены."

    update.message.reply_text(message_text)


def check_user_in_db(user_id):
    return Customer.objects.filter(telegram_id=user_id).exists()


def request_phone_number(update: Update, context: CallbackContext, chat_id):
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Поделиться номером телефона", request_contact=True)]],
                                   one_time_keyboard=True)
    context.bot.send_message(chat_id=chat_id, text="Пожалуйста, поделитесь своим номером телефона для завершения регистрации.",
                             reply_markup=keyboard)


def handle_contact(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    contact = update.effective_message.contact
    phone_number = contact.phone_number
    first_name = contact.first_name if contact.first_name else ''
    last_name = contact.last_name if contact.last_name else ''

    customer, created = Customer.objects.get_or_create(
        phone=phone_number,
        defaults={'first_name': first_name, 'last_name': last_name, 'telegram_id': chat_id},
    )

    if created:
        context.bot.send_message(chat_id=chat_id, text="Вы успешно зарегистрированы!")
    else:
        context.bot.send_message(chat_id=chat_id, text="Вы уже зарегистрированы!")

    # save_appointment_from_user_data(update, context)


def register_user(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    contact = update.effective_message.contact
    phone_number = contact.phone_number
    first_name = contact.first_name if contact.first_name else ''
    last_name = contact.last_name if contact.last_name else ''

    customer, created = Customer.objects.get_or_create(
        phone=phone_number,
        defaults={'first_name': first_name, 'last_name': last_name, 'telegram_id': chat_id},
    )
    if created:
        context.bot.send_message(chat_id=chat_id, text="Вы успешно зарегистрированы!")
        save_appointment_from_user_data(update, context)
    else:
        context.bot.send_message(chat_id=chat_id, text="Вы уже зарегистрированы!")
        show_big_keyboard(update, context, chat_id)


def main():
    updater = Updater("6506598877:AAE0D2T8MygorZoF6dxNJmYspSI-lwyKyDo", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text("Записаться"), show_main_menu))
    dp.add_handler(MessageHandler(Filters.text("Мои записи"), show_my_appointments))
    dp.add_handler(MessageHandler(Filters.text("Салоны"), show_salons))
    dp.add_handler(MessageHandler(Filters.text("Мастера"), show_staffs))
    dp.add_handler(MessageHandler(Filters.text("Услуги"), show_services))
    dp.add_handler(MessageHandler(Filters.text("Администратор"), show_admin_message))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.contact, handle_contact))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
