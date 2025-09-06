from flask import Flask, render_template, request, jsonify
from models import db, Chat
from config import DATABASE_URL, OPENROUTER_API_KEY
from openai import OpenAI
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar banco
db.init_app(app)

# Configuração da API OpenRouter - NOVA SINTAXE
client = None
if OPENROUTER_API_KEY:
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        # Buscar histórico
        history = Chat.query.order_by(Chat.timestamp).all()
        messages = [
            {"role": "system", "content": "Você é um assistente útil."},
        ]
        for h in history:
            messages.append({"role": "user", "content": h.user_message})
            messages.append({"role": "assistant", "content": h.bot_response})
        messages.append({"role": "user", "content": user_message})

        # Chamar API - NOVA SINTAXE
        if client and OPENROUTER_API_KEY:
            try:
                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat-v3.1:free",
                    messages=messages
                )
                bot_response = response.choices[0].message.content.strip()
            except Exception as e:
                bot_response = f"Erro na API: {str(e)}"
        else:
            bot_response = "API key não configurada"

        # Salvar no banco
        chat_entry = Chat(user_message=user_message, bot_response=bot_response)
        db.session.add(chat_entry)
        db.session.commit()

        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"response": f"Erro interno: {str(e)}"}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)