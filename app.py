import requests
import json
import os
from flask import Flask, render_template, request, jsonify
from models import db, Chat
from config import DATABASE_URL

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# URL do servidor LLaMA local
LLAMA_URL = "http://141.148.138.218:8082/completion"

def chat_com_llama_local(messages):
    """Chama o modelo LLaMA local via API"""
    prompt = formatar_prompt_mistral(messages)
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "n_predict": 512,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(LLAMA_URL, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()["content"]
    except requests.exceptions.ConnectionError as e:
        return f"Erro de conexão ao chamar LLaMA local: {str(e)}"
    except requests.exceptions.Timeout as e:
        return f"Timeout ao chamar LLaMA local: {str(e)}"
    except Exception as e:
        return f"Erro desconhecido ao chamar LLaMA local: {str(e)}"

def formatar_prompt_mistral(messages):
    """Formata mensagens no formato do Mistral"""
    prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            prompt += f"{msg['content']}\n"
        elif msg["role"] == "user":
            prompt += f"[INST] {msg['content']} [/INST]\n"
        elif msg["role"] == "assistant":
            prompt += f"{msg['content']}\n"
    return prompt

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

        # Chamar LLaMA local
        bot_response = chat_com_llama_local(messages)

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
