FROM python:3.11-slim

WORKDIR /app

# Dependências mínimas — FastAPI para o endpoint, google-cloud-firestore
# opcional (só falha se o client não estiver no requirements do deploy).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Cloud Run injeta PORT (default 8080)
ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
