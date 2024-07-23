import sqlite3


def create_clients_table():
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            first_name TEXT,
            phone TEXT
        )
    ''')
    conn.commit()
    conn.close()


def is_client_in_database(user_id):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('SELECT first_name FROM clients WHERE telegram_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def add_client_to_database(user_id, first_name, phone):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO clients (telegram_id, first_name, phone) VALUES (?, ?, ?)',
                   (user_id, first_name, phone))
    conn.commit()
    conn.close()

from telegram import Update

def download_document(chat_id, bot):
    bot.send_document(chat_id=chat_id, document=open('soglasie.pdf', 'rb'))

# def download_document(update, context):
#     """Отправляем документ клиенту"""
#     context.bot.send_document(chat_id=update.effective_chat.id,
#                               document=open('soglasie.pdf', 'rb'))
