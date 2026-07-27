import logging
import psycopg
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Доставка", callback_data="category_Доставка")],
        [InlineKeyboardButton("↩️ Возврат", callback_data="category_Возврат")],
        [InlineKeyboardButton("💳 Оплата", callback_data="category_Оплата")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Привет! 👋\nВыберите категорию, чтобы получить ответы на вопросы:",
        reply_markup=reply_markup
    )

async def get_faq_by_category(category: str):
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT f.question, f.answer FROM faq f
        JOIN categories c ON f.category_id = c.id
        WHERE c.name = %s
    """, (category,))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return results

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    category = query.data.replace("category_", "")
    results = await get_faq_by_category(category)
    
    if results:
        text = f"📚 *{category}*\n\n"
        for q, a in results:
            text += f"❓ {q}\n💬 {a}\n\n"
        await query.edit_message_text(text, parse_mode='Markdown')
    else:
        await query.edit_message_text(f"Нет вопросов по категории {category}")

async def get_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    results = await get_faq_by_category(category)
    
    if results:
        text = f"📚 {category}:\n\n"
        for q, a in results:
            text += f"❓ {q}\n💬 {a}\n\n"
        await update.message.reply_text(text)
    else:
        await update.message.reply_text(f"Нет вопросов по категории {category}")

async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_faq(update, context, "Доставка")

async def returns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_faq(update, context, "Возврат")

async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_faq(update, context, "Оплата")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()
    
    user_text = update.message.text.lower()
    
    cur.execute("""
        SELECT f.question, f.answer, c.name FROM faq f
        JOIN categories c ON f.category_id = c.id
        WHERE LOWER(f.question) LIKE %s
    """, (f"%{user_text}%",))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    if results:
        text = "Найденные ответы:\n\n"
        for q, a, cat in results:
            text += f"📂 {cat}\n❓ {q}\n💬 {a}\n\n"
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("Ответ не найден. Попробуйте /delivery, /returns или /payment")

def main():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("delivery", delivery))
    app.add_handler(CommandHandler("returns", returns))
    app.add_handler(CommandHandler("payment", payment))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^category_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
