from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from actions_database import download_document

# Функция-обработчик команды /start
def start(update, context):
    user = update.message.from_user
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Прочитать условия", callback_data='read_terms')],
    ])
    update.message.reply_text(
        f'Здравствуйте, {user.first_name}\nДля регистрации прочитайте условия',
        reply_markup=keyboard
    )

# Функция-обработчик нажатия кнопки встроенной клавиатуры
def button(update, context):
    query = update.callback_query
    if query.data == 'read_terms':
        download_document(query.message.chat_id, context.bot)
        # Остальной код для вывода кнопок "Согласен" и "Отказаться"
        pass

# Создаем экземпляр бота и регистрируем обработчики
updater = Updater(token='', use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(button))

# Запускаем бота
updater.start_polling()
