import os
import json
from dotenv import load_dotenv
from utils.milvus_client import MilvusClient
from pymilvus import utility
from tqdm import tqdm

load_dotenv()

def load_medical_data(file_path="data/medical_data.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def initialize_milvus():
    print("Инициализация Milvus...")
    milvus_client = MilvusClient()
    data = load_medical_data()

    if not utility.has_collection(milvus_client.qa_collection_name):
        print("Создание коллекции...")
        collection = milvus_client.create_qa_collection()

        print("Вставка данных...")
        batch_size = 10
        for i in tqdm(range(0, len(data), batch_size), desc="Загрузка данных"):
            batch = data[i:i + batch_size]
            milvus_client.insert_qa_data(collection, batch)

        print("Создание индекса...")
        milvus_client.create_index(collection)
    else:
        print("Коллекция уже существует, подключаемся к ней...")

if __name__ == "__main__":
    initialize_milvus()
