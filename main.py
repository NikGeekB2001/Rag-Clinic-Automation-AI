import os
import json
from dotenv import load_dotenv
from utils.milvus_client import MilvusClient
from tqdm import tqdm

load_dotenv()

def load_medical_data(file_path="data/medical_data.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def initialize_milvus():
    print("Инициализация Milvus...")
    milvus_client = MilvusClient()
    from pymilvus import utility
    try:
        if utility.has_collection(milvus_client.qa_collection_name):
            print(f"Найдена существующая коллекция '{milvus_client.qa_collection_name}'. Удаляем...")
            utility.drop_collection(milvus_client.qa_collection_name)
            print("Коллекция удалена.")
    except Exception as e:
        print(f"Ошибка при удалении коллекции: {e}")
    data = load_medical_data()
    qa_data = [doc for doc in data if "options" not in doc]
    print("Создание коллекции для вопросов-ответов...")
    qa_collection = milvus_client.create_qa_collection()
    print(f"Коллекция создана с размерностью {milvus_client.embedding_model.get_sentence_embedding_dimension()}")
    print("Вставка данных в коллекцию вопросов-ответов...")
    milvus_client.insert_qa_data(qa_collection, qa_data)
    print(f"Вставлено {len(qa_data)} записей")
    milvus_client.create_index(qa_collection)
    print("Индекс создан и коллекция загружена")
    return milvus_client

milvus_client = initialize_milvus()

def search(query, k=3):
    print(f"Обработка запроса: {query}")
    answer, results = milvus_client.search_and_generate(query, k)
    print(f"Найдено {len(results)} релевантных результатов")
    return answer, results

if __name__ == "__main__":
    query = "Как оформить больничный лист?"
    print(f"Поиск по запросу: {query}")
    answer, results = search(query)
    print(f"Сгенерированный ответ: {answer}")
