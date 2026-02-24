# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости для psycopg2 и других библиотек
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Указываем порт, который будет слушать приложение
EXPOSE 8000

# Команда по умолчанию – запуск Gunicorn (или можно runserver для разработки)
# Команда по умолчанию – запуск Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
# Альтернатива для разработки (раскомментировать при необходимости):
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]