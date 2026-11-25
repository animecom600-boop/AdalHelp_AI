import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

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
                            "Адамды мұқият тыңда, айыптама және қауіпсіз "
                            "шешімдерді ұсын. Сен кәсіби психолог немесе дәрігер емессің."
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
            return jsonify({"error": "AI қызметінде уақытша қате пайда болды."}), 502

        answer = response.json()["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})

    except requests.RequestException:
        return jsonify({"error": "AI серверіне қосылу мүмкін болмады."}), 502
    except (KeyError, ValueError):
        return jsonify({"error": "AI жауабын оқу мүмкін болмады."}), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
