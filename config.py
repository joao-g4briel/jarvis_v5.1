import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/chatbot")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")