# Первая ступень: сборка
FROM python:3.12-slim AS builder

WORKDIR /app

# Настройка pip для более надежной загрузки
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_CACHE_DIR=/tmp/pip-cache \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Вторая ступень: запуск
FROM python:3.12-slim

WORKDIR /app

# Копируем только необходимые файлы
COPY --from=builder /root/.local /root/.local
COPY . .

# Устанавливаем зависимости
ENV PATH=/root/.local/bin:$PATH

# Запуск приложения
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
