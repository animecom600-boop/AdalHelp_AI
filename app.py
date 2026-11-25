import os
import re
import time
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv(".env")

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
SUPABASE_REST_URL = f"{SUPABASE_URL}/rest/v1/messages"

chat_limits = {}
CHAT_COOLDOWN = 10


def supabase_headers():
    return {
        "apikey": SUPABASE_SECRET_KEY,
        "Content-Type": "application/json"
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/ai", methods=["POST"])
def ai():
    if not GROQ_API_KEY:
        return jsonify({"error": "AI кілті бапталмаған."}), 500

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Хабарлама бос болмауы керек."}), 400

    if len(message) > 4000:
        return jsonify({"error": "Хабарлама тым ұзын."}), 400

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen/qwen3.8-27b",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Сен AdalHelp AI көмекшісісің. "
                            "Қазақ тілінде жылы, сабырлы және түсінікті жауап бер. "
                            "Адамды айыптама, қауіпсіз шешімдерді ұсын. "
                            "Сен кәсіби психолог немесе дәрігер емессің."
                        )
                    },
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 700
            },
            timeout=40
        )

        if response.status_code != 200:
            return jsonify({"error": "AI қызметінде уақытша қате."}), 502

        answer = response.json()["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})

    except requests.RequestException:
        return jsonify({"error": "AI серверіне қосылу мүмкін болмады."}), 502
    except (KeyError, ValueError):
        return jsonify({"error": "AI жауабын оқу мүмкін болмады."}), 502


@app.route("/api/chat", methods=["GET"])
def get_chat():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        return jsonify({"error": "Чат базасы бапталмаған."}), 500

    try:
        response = requests.get(
            SUPABASE_REST_URL,
            headers=supabase_headers(),
            params={
                "select": "id,nickname,content,created_at",
                "status": "eq.approved",
                "order": "created_at.desc",
                "limit": "50"
            },
            timeout=15
        )

        if response.status_code != 200:
            return jsonify({"error": "Хабарламаларды жүктеу мүмкін болмады."}), 502

        return jsonify({"messages": response.json()})

    except requests.RequestException:
        return jsonify({"error": "Чат серверіне қосылу мүмкін болмады."}), 502


@app.route("/api/chat", methods=["POST"])
def send_chat():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        return jsonify({"error": "Чат базасы бапталмаған."}), 500

    data = request.get_json(silent=True) or {}
    nickname = str(data.get("nickname", "")).strip()
    content = str(data.get("content", "")).strip()

    if not nickname or not content:
        return jsonify({"error": "Лақап ат пен хабарламаны толтыр."}), 400

    if len(nickname) > 20 or len(content) > 500:
        return jsonify({"error": "Мәтін тым ұзын."}), 400

    if re.search(r"(?i)(https?://|www\.|t\.me/|@[a-zA-Z0-9_]{5,})", content):
        return jsonify({"error": "Сілтемелер мен байланыс деректерін жіберуге болмайды."}), 400

    now = time.time()
    client_id = request.remote_addr or "unknown"
    last_sent = chat_limits.get(client_id, 0)

    if now - last_sent < CHAT_COOLDOWN:
        return jsonify({"error": "Келесі хабарламаны 10 секундтан кейін жібер."}), 429

    chat_limits[client_id] = now

    try:
        response = requests.post(
            SUPABASE_REST_URL,
            headers={
                **supabase_headers(),
                "Prefer": "return=minimal"
            },
            json={
                "nickname": nickname,
                "content": content,
                "status": "approved"
            },
            timeout=15
        )

if response.status_code not in (200, 201, 204):
    print("SUPABASE ERROR:", response.status_code, response.text[:500])
    chat_limits.pop(client_id, None)
    return jsonify({"error": "Хабарламаны сақтау мүмкін болмады."}), 502
        return jsonify({
            "success": True,
            "message": "Хабарлама модерацияға жіберілді."
        }), 201

    except requests.RequestException:
        chat_limits.pop(client_id, None)
        return jsonify({"error": "Чат серверіне қосылу мүмкін болмады."}), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
