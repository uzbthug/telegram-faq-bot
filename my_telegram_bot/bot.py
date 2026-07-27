import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Включим логирование для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === БАЗА ЗНАНИЙ (FAQ) ===
faq_data = {
    "delivery": {
        "title": "📦 Доставка",
        "text": (
            "Мы доставляем заказы по всей стране.\n\n"
            "⏱ Сроки доставки:\n"
            "• Москва и МО: 1-2 дня\n"
            "• Регионы: 3-7 дней\n\n"
            "💰 Стоимость:\n"
            "• От 5000 руб. — бесплатно\n"
            "• Менее 5000 руб. — 300 руб."
        )
    },
    "return": {
        "title": "🔄 Возврат",
        "text": (
            "Вы можете вернуть товар в течение 14 дней.\n\n"
            "Условия возврата:\n"
            "• Товар не был в использовании\n"
            "• Сохранена упаковка и бирки\n"
            "• Есть чек или заказ в системе\n\n"
            "Для оформления возврата напишите @support_bot"
        )
    },
    "payment": {
        "title": "💳 Оплата",
        "text": (
            "Мы принимаем следующие способы оплаты:\n\n"
            "• Банковские карты (Visa, MasterCard, МИР)\n"
            "• Электронные кошельки (ЮMoney, Qiwi)\n"
            "• Оплата при получении (наложенный платеж)\n\n"
            "Все платежи защищены по стандарту PCI DSS."
        )
    }
}

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с кнопками категорий."""
    keyboard = [
        [InlineKeyboardButton("📦 Доставка", callback_data="delivery")],
        [InlineKeyboardButton("🔄 Возврат", callback_data="return")],
        [InlineKeyboardButton("💳 Оплата", callback_data="payment")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Привет! Я бот службы поддержки.\n\n"
        "Выберите категорию, чтобы получить информацию:",
        reply_markup=reply_markup
    )

# Обработчик нажатий на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на inline-кнопки и показывает соответствующий FAQ."""
    query = update.callback_query
    await query.answer()  # Подтверждаем получение нажатия
    
    category = query.data
    
    if category in faq_data:
        data = faq_data[category]
        # Формируем клавиатуру с кнопкой "Назад"
        keyboard = [[InlineKeyboardButton("🔙 Назад к меню", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"*{data['title']}*\n\n{data['text']}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    elif category == "back":
        # Возвращаем главное меню
        keyboard = [
            [InlineKeyboardButton("📦 Доставка", callback_data="delivery")],
            [InlineKeyboardButton("🔄 Возврат", callback_data="return")],
            [InlineKeyboardButton("💳 Оплата", callback_data="payment")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👋 Привет! Я бот службы поддержки.\n\n"
            "Выберите категорию, чтобы получить информацию:",
            reply_markup=reply_markup
        )

def main():
    """Запускает бота."""
    # TODO: Замените 'YOUR_BOT_TOKEN' на ваш токен от BotFather
    token = "YOUR_BOT_TOKEN"
    
    if token == "YOUR_BOT_TOKEN":
        print("❗ ОШИБКА: Вы не указали токен бота!")
        print("Пожалуйста, замените 'YOUR_BOT_TOKEN' в файле bot.py на ваш токен.")
        print("Токен можно получить у @BotFather в Telegram.")
        return
    
    # Создаём приложение
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Запускаем бота
    print("✅ Бот запущен... (нажмите Ctrl+C для остановки)")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
