FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primeiro para otimizar cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY . .

# Rodar o app
CMD ["python", "app.py"]