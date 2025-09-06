from flask_sqlalchemy import SQLAlchemy

# Criar o objeto db global
db = SQLAlchemy()

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())