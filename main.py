from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_conn():
    DATABASE_URL = os.environ.get("postgresql://serverless_db_t9oz_user:Y0QFDk5rZ287tYn1uUz0id1CNvbK8eWB@dpg-d738ksi4d50c73fjfjbg-a.oregon-postgres.render.com/serverless_db_t9oz")

    if not DATABASE_URL:
        raise Exception("DATABASE_URL not found")

    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(DATABASE_URL, sslmode="require")


@app.route("/")
def home():
    return "API is running 🚀"


def init_db():
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

init_db()


@app.route('/save', methods=['POST'])
def save_message():
    try:
        data = request.get_json()
        message = data.get('message', '') if data else ''

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO messages (content) VALUES (%s)", (message,))
                conn.commit()

        return jsonify({"status": "saved", "message": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

        messages = [{"id": r[0], "text": r[1], "time": r[2].isoformat()} for r in rows]

        return jsonify(messages)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)