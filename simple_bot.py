import telebot
from telebot import types

# ВСТАВЬТЕ СЮДА ВАШ ТОКЕН ОТ BOTFATHER
TOKEN = "СЮДА_ВСТАВИТЬ_ВАШ_ТОКЕН"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📅 Записаться на прием")
    btn2 = types.KeyboardButton("👨‍⚕️ Наши врачи")
    btn3 = types.KeyboardButton("📞 Контакты")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(message.chat.id, 
                     f"Здравствуйте, {message.from_user.first_name}!\nЯ бот клиники. Чем могу помочь?", 
                     reply_markup=markup)

@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "📅 Записаться на прием":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Терапевт")
        btn2 = types.KeyboardButton("Окулист")
        btn3 = types.KeyboardButton("Стоматолог")
        btn4 = types.KeyboardButton("⬅️ Назад")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, "Выберите врача:", reply_markup=markup)
    
    elif message.text == "👨‍⚕️ Наши врачи":
        bot.send_message(message.chat.id, "У нас работают лучшие специалисты города!")
    
    elif message.text == "📞 Контакты":
        bot.send_message(message.chat.id, "Наш телефон: +7 (999) 000-00-00\nАдрес: ул. Примерная, 1")
        
    elif message.text == "⬅️ Назад":
        start(message)
        
    elif message.text in ["Терапевт", "Окулист", "Стоматолог"]:
        bot.send_message(message.chat.id, f"Вы выбрали: {message.text}.\nНапишите желаемую дату и время (например: Завтра в 15:00), и я передам заявку администратору.")
        # Здесь можно добавить логику сохранения заявки
        
    else:
        bot.send_message(message.chat.id, "Я пока не понимаю эту команду. Нажмите /start, чтобы начать заново.")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
