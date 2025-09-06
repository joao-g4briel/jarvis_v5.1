from flask import Flask, render_template, request, jsonify
from models import db, Chat
from config import DATABASE_URL, OPENROUTER_API_KEY
import requests
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar banco
db.init_app(app)

def chat_com_openrouter(messages):
    """Função para se comunicar com a API do OpenRouter"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://jarvis-chatbot.coolify.app",  # Substitua pela URL real do seu app
            "X-Title": "Jarvis Chatbot"
        }
        
        payload = {
            "model": "deepseek/deepseek-chat-v3.1:free",
            "messages": messages
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Erro na API: {str(e)}"

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
            {"role": "system", "content": "Você é um assistente útil chamado Jarvis, especializado em ajudar estudantes."},
        ]
        for h in history:
            messages.append({"role": "user", "content": h.user_message})
            messages.append({"role": "assistant", "content": h.bot_response})
        messages.append({"role": "user", "content": user_message})

        # Chamar API
        if OPENROUTER_API_KEY:
            bot_response = chat_com_openrouter(messages)
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
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))