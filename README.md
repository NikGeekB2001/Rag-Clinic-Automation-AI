# Rag Clinic Automation AI

## Описание проекта
Проект представляет собой систему автоматизации клиники с использованием RAG (Retrieval-Augmented Generation) и Milvus для векторного поиска. Включает веб-интерфейс на Streamlit и сервисы Milvus, MinIO и etcd, запущенные через Docker Compose.

### Основные возможности
- Векторный поиск медицинских данных с использованием Milvus.
- Генерация ответов на основе RAG модели.
- Веб-интерфейс для взаимодействия с системой.
- Интеграция с Docker для легкого развертывания.

### Архитектура
- **Frontend:** Streamlit UI для пользовательского интерфейса.
- **Backend:** Python сервисы для обработки запросов и взаимодействия с Milvus.
- **База данных:** Milvus для векторного хранения и поиска.
- **Хранение:** MinIO для хранения файлов.
- **Конфигурация:** etcd для управления конфигурациями.

## Как запустить проект

### Требования
- Docker и Docker Compose должны быть установлены на вашей машине.
- Порт 8501 должен быть свободен для запуска Streamlit UI.

### Запуск проекта

1. Клонируйте репозиторий и перейдите в директорию проекта:
   ```bash
   git clone <repository-url>
   cd Rag-Clinic-Automation-AI
   ```

2. Запустите контейнеры Docker:
   ```bash
   docker-compose up -d
   ```

3. Установите зависимости Python:
   ```bash
   pip install -r requirements.txt
   ```

4. Инициализируйте Milvus с медицинскими данными:
   ```bash
   source venv/Scripts/activate && python init_milvus.py
   ```

5. Запустите основной сервис:
   ```bash
   source venv/Scripts/activate && python main.py
   ```

6. Запустите Streamlit UI:
   ```bash
   source venv/Scripts/activate && streamlit run app.py
   ```

7. Для перезапуска приложения используйте:
   ```bash
   docker-compose restart rag-app
   ```

8. Убедитесь, что Milvus запущен (например, через docker-compose):
   ```bash
   docker-compose ps
   ```

9. Откройте веб-интерфейс Streamlit в браузере по адресу:
   ```
   http://localhost:8501
   ```

### Остановка проекта
Для остановки и удаления контейнеров выполните:
```bash
docker-compose down
```
## Структура проекта
- `app.py` — основной файл Streamlit UI.
- `docker-compose.yml` — конфигурация Docker Compose для запуска сервисов.
- `utils/milvus_client.py` — клиент для работы с Milvus.
- `init_milvus.py` — инициализация Milvus.
- `main.py` — основной backend код (если есть).
- `requirements.txt` — зависимости Python.

## Тестирование
- Запустите UI и проверьте основные функции.
- При необходимости можно добавить автоматические тесты.

---

