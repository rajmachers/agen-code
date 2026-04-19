FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

COPY app ./app

EXPOSE 8020

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020", "--loop", "asyncio", "--http", "h11"]
