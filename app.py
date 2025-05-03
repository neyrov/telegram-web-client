import os
from flask import Flask, render_template, request, redirect, session, url_for
import telebot

# Получение переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")  # Заменить на твой пароль через переменные окружения

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Для безопасных сессий

# Хранение сообщений
messages = []

# Обработчик сообщений Telegram
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    messages.append({
        'chat_id': message.chat.id,
        'from': message.from_user.first_name,
        'text': message.text
    })

# Логин
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:  # Сравнение с паролем из переменной окружения
            session['authenticated'] = True
            return redirect('/')
        else:
            return render_template('login.html', error="Неверный пароль.")
    return render_template('login.html')

# Главная страница
@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        chat_id = request.form['chat_id']
        text = request.form['text']
        bot.send_message(chat_id, text)
        return redirect('/')
    
    # Показываем последние 50 сообщений
    return render_template('index.html', messages=reversed(messages[-50:]))

# Выход
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect('/login')

if __name__ == '__main__':
    from threading import Thread
    # Запуск бота в отдельном потоке
    Thread(target=bot.polling, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
