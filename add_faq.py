import psycopg
import os

conn = psycopg.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

categories = ["Доставка", "Возврат", "Оплата"]
for cat in categories:
    cur.execute("INSERT INTO categories (name) VALUES (%s) ON CONFLICT DO NOTHING", (cat,))

faq_items = [
    ("Доставка", "Как долго доставка?", "Доставка занимает 3-5 рабочих дней."),
    ("Доставка", "Какая стоимость доставки?", "Доставка бесплатна при заказе от 1000 руб."),
    ("Доставка", "Куда вы доставляете?", "Мы доставляем по всей России."),
    ("Возврат", "Как вернуть товар?", "Вы можете вернуть товар в течение 14 дней с момента покупки."),
    ("Возврат", "Какой процесс возврата?", "Свяжитесь с поддержкой, отправьте товар обратно, получите возврат денег."),
    ("Возврат", "Есть ли комиссия за возврат?", "Нет, возврат полностью бесплатен."),
    ("Оплата", "Какие способы оплаты?", "Мы принимаем карты, Яндекс.Касса, PayPal."),
    ("Оплата", "Безопасна ли оплата?", "Да, все платежи защищены SSL шифрованием."),
    ("Оплата", "Можно ли платить в рассрочку?", "Да, доступна рассрочка через Яндекс.Касса."),
]

for category, question, answer in faq_items:
    cur.execute("SELECT id FROM categories WHERE name = %s", (category,))
    result = cur.fetchone()
    if result:
        cat_id = result[0]
        cur.execute("INSERT INTO faq (category_id, question, answer) VALUES (%s, %s, %s)", (cat_id, question, answer))

conn.commit()
cur.close()
conn.close()
print("✅ FAQ добавлены!")
