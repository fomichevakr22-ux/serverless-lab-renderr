from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Подключение к БД
DATABASE_URL = os.environ.get("DATABASE_URL")

conn = None

if DATABASE_URL:
    try:
        # фикс для Render (иногда postgres:// вместо postgresql://)
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

        conn = psycopg2.connect(DATABASE_URL)
        print("✅ DB CONNECTED")

        # Создание таблицы
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            conn.commit()

    except Exception as e:
        print("❌ DB ERROR:", e)
        conn = None
else:
    print("❌ DATABASE_URL not found")


# Главная страница (чтобы не было 404)
@app.route("/")
def home():
    return "API is running 🚀"


# Сохранить сообщение
@app.route('/save', methods=['POST'])
def save_message():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    data = request.get_json()
    message = data.get('message', '') if data else ''

    with conn.cursor() as cur:
        cur.execute("INSERT INTO messages (content) VALUES (%s)", (message,))
        conn.commit()

    return jsonify({"status": "saved", "message": message})


# Получить сообщения
@app.route('/messages')
def get_messages():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, content, created_at 
            FROM messages 
            ORDER BY id DESC 
            LIMIT 10
        """)
        rows = cur.fetchall()

    messages = [
        {"id": r[0], "text": r[1], "time": r[2].isoformat()}
        for r in rows
    ]

    return jsonify(messages)


# Запуск сервера (ВАЖНО для Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)