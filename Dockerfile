FROM python:3.11-slim

# Variables de entorno para optimizar Python y mejorar logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000


CMD ["gunicorn", "--chdir", "/app", "app.main:app", "--bind", "0.0.0.0:5000", "--workers", "3"]

