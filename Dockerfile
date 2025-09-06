FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primeiro para otimizar cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY . .

<<<<<<< HEAD
# Rodar o app
CMD ["python", "app.py"]
=======
CMD ["python", "app.py"]
>>>>>>> 34d87de888aac5469a504a997f3b8f27b9d01e85
