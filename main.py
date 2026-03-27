from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)


# 🔌 Функция подключения к БД (ВАЖНО: новое соединение каждый раз)
def get_conn():
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if not DATABASE_URL:
        raise Exception("DATABASE_URL not found")

    # фикс для Render
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(DATABASE_URL, sslmode="require")


# 🏠 Главная страница
@app.route("/")
def home():
    return "API is running 🚀"


# 🛠 Создание таблицы (один раз при старте)
def init_db():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                conn.commit()
        print("✅ DB initialized")
    except Exception as e:
        print("❌ DB INIT ERROR:", e)


init_db()


# 📩 Сохранить сообщение
@app.route('/save', methods=['POST'])
def save_message():
    try:
        data = request.get_json()
        message = data.get('message', '') if data else ''

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO messages (content) VALUES (%s)",
                    (message,)
                )
                conn.commit()

        return jsonify({"status": "saved", "message": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📥 Получить сообщения
@app.route('/messages')
def get_messages():
    try:
        with get_conn() as conn:
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🚀 Запуск (обязательно для Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)