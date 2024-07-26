import telegram
from telegram.ext import Updater, CommandHandler

# Обработчик команды /start
def start(update, context):
    # Запросить номер телефона пользователя
    keyboard = [[telegram.KeyboardButton(text="Share Contact", request_contact=True)]]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please share your contact:", reply_markup=reply_markup)

# Обработчик получения номера телефона
def handle_contact(update, context):
    contact = update.message.contact
    phone_number = contact.phone_number
    print("Phone number:", phone_number)

# Создание и запуск бота
updater = Updater(token='YOUR_TELEGRAM_BOT_TOKEN', use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(telegram.ext.Filters.contact, handle_contact))
updater.start_polling()
