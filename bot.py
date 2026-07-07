import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db():
    """Инициализация таблиц в БД"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id SERIAL PRIMARY KEY,
            category_id INTEGER NOT NULL REFERENCES categories(id),
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_category ON faq(category_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_question ON faq USING GIN(to_tsvector('russian', question))")
    
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Database initialized")

def get_categories():
    """Получить все категории"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return categories

def get_questions_by_category(category_id):
    """Получить вопросы по категории"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, question, answer FROM faq WHERE category_id = %s ORDER BY question", (category_id,))
    questions = cur.fetchall()
    cur.close()
    conn.close()
    return questions

def search_faq(query):
    """Поиск в FAQ по вопросу"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT f.id, f.question, f.answer, c.name as category
        FROM faq f
        JOIN categories c ON f.category_id = c.id
        WHERE to_tsvector('russian', f.question) @@ plainto_tsquery('russian', %s)
        LIMIT 1
    """, (query,))
    
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - показать категории"""
    categories = get_categories()
    
    if not categories:
        await update.message.reply_text("❌ Категории не найдены. Свяжитесь с администратором.")
        return
    
    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(cat['name'], callback_data=f"cat_{cat['id']}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Добро пожаловать! Выберите категорию для просмотра FAQ:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    await update.message.reply_text(
        "Я помогу вам найти ответ на вопрос!\n\n"
        "Используйте /start чтобы увидеть категории FAQ\n"
        "Или просто напишите ваш вопрос - я попытаюсь найти ответ"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений - поиск в FAQ"""
    user_question = update.message.text
    
    result = search_faq(user_question)
    
    if result:
        await update.message.reply_text(
            f"📚 <b>{result['category']}</b>\n\n"
            f"<b>Q:</b> {result['question']}\n"
            f"<b>A:</b> {result['answer']}",
            parse_mode="HTML"
        )
    else:
        keyboard = [[InlineKeyboardButton("Показать категории", callback_data="show_categories")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "😕 Я не нашел ответ на ваш вопрос.\n\n"
            "Попробуйте выбрать категорию или переформулируйте вопрос.",
            reply_markup=reply_markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "show_categories":
        categories = get_categories()
        keyboard = []
        for cat in categories:
            keyboard.append([InlineKeyboardButton(cat['name'], callback_data=f"cat_{cat['id']}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Выберите категорию:",
            reply_markup=reply_markup
        )
    elif query.data.startswith("cat_"):
        category_id = int(query.data.replace("cat_", ""))
        questions = get_questions_by_category(category_id)
        
        if not questions:
            await query.edit_message_text("❌ Вопросы не найдены")
            return
        
        keyboard = []
        for q in questions:
            keyboard.append([InlineKeyboardButton(q['question'][:50] + "...", callback_data=f"q_{q['id']}")])
        keyboard.append([InlineKeyboardButton("← Назад", callback_data="show_categories")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"📚 Выберите вопрос:",
            reply_markup=reply_markup
        )
    elif query.data.startswith("q_"):
        question_id = int(query.data.replace("q_", ""))
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT f.question, f.answer, c.name, c.id as category_id
            FROM faq f
            JOIN categories c ON f.category_id = c.id
            WHERE f.id = %s
        """, (question_id,))
        q = cur.fetchone()
        cur.close()
        conn.close()
        
        if q:
            keyboard = [[InlineKeyboardButton("← Назад к категории", callback_data=f"cat_{q['category_id']}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"📚 <b>{q['name']}</b>\n\n"
                f"<b>Q:</b> {q['question']}\n"
                f"<b>A:</b> {q['answer']}",
                reply_markup=reply_markup,
                parse_mode="HTML"
            )

async def main():
    """Запуск бота"""
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN не установлен!")
    
    init_db()
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
