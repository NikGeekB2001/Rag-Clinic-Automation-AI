from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
import os
import json
import re
from dotenv import load_dotenv
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.prompts import MedicalPromptManager

load_dotenv()

class MilvusClient:
    def __init__(self):
        self.host = os.getenv("MILVUS_HOST", "standalone")
        self.port = os.getenv("MILVUS_PORT", "19530")
        self.qa_collection_name = "medical_qa"
        self.embedding_model = SentenceTransformer('intfloat/multilingual-e5-large')
        self.qa_model_name = "Den4ikAI/rubert_large_squad_2"
        self.qa_tokenizer = AutoTokenizer.from_pretrained(self.qa_model_name)
        self.qa_model = AutoModelForQuestionAnswering.from_pretrained(self.qa_model_name)
        self.vectorizer = TfidfVectorizer()
        self.prompt_manager = MedicalPromptManager()
        self.connect()

    def connect(self):
        print("Подключение к Milvus...")
        connections.connect("default", host=self.host, port=self.port)

    def load_data(self, file_path="data/medical_data.json"):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def create_qa_collection(self):
        if utility.has_collection(self.qa_collection_name):
            utility.drop_collection(self.qa_collection_name)
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="question", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="answer", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
        ]
        schema = CollectionSchema(fields, description="Medical QA collection")
        collection = Collection(self.qa_collection_name, schema)
        return collection

    def insert_qa_data(self, collection, data):
        ids = [doc["id"] for doc in data]
        questions = [doc["question"] for doc in data]
        answers = [doc["answer"] for doc in data]
        urls = [doc["url"] for doc in data]
        categories = [doc["category"] for doc in data]
        texts = [f"Вопрос: {q} Ответ: {a}" for q, a in zip(questions, answers)]
        embeddings = self.embedding_model.encode(texts).tolist()
        collection.insert([
            ids,
            embeddings,
            questions,
            answers,
            urls,
            categories,
        ])
        collection.flush()

    def create_index(self, collection):
    print("Создание индекса HNSW...")
    index_params = {
        "metric_type": "COSINE",  # Лучше для текстовых данных
        "index_type": "HNSW",
        "params": {
            "M": 32,               # Увеличили с 16 до 32 для лучшей точности
            "efConstruction": 500  # Увеличили с 256 до 500 для лучшего качества индекса
        }
    }
    collection.create_index("vector", index_params)
    collection.load()


    def search_qa(self, query, k=5):
        query_embedding = self.embedding_model.encode([f"Вопрос: {query}"]).tolist()
        collection = Collection(self.qa_collection_name)
        search_params = {"metric_type": "COSINE", "params": {"ef": 128}}
        results = collection.search(
            data=[query_embedding[0]],
            anns_field="vector",
            param=search_params,
            limit=k,
            output_fields=["question", "answer", "url", "category"]
        )
        return results[0]

    def calculate_similarity(self, query, results):
        query_texts = [query] * len(results)
        result_texts = [hit.entity.question + ' ' + hit.entity.answer for hit in results]

        tfidf_matrix = self.vectorizer.fit_transform(query_texts + result_texts)
        query_vectors = tfidf_matrix[:len(results)]
        result_vectors = tfidf_matrix[len(results):]

        similarities = cosine_similarity(query_vectors, result_vectors).diagonal()
        print(f"Similarities: {similarities}")

        scored_results = sorted(
            zip(results, similarities),
            key=lambda x: x[1],
            reverse=True
        )

        return [result for result, score in scored_results if score > 0.0]

    def filter_relevant_results(self, query, results):
        query_lower = query.lower()
        relevant_results = []

        filtered_results = self.calculate_similarity(query, results)
        print(f"Filtered by similarity: {len(filtered_results)}")

        for hit in filtered_results:
            question = hit.entity.question.lower()
            answer = hit.entity.answer.lower()

            if any(word in answer for word in query_lower.split() if len(word) > 3):
                relevant_results.append(hit)

        print(f"Relevant results: {len(relevant_results)}")
        return relevant_results if relevant_results else filtered_results[:1]

    def generate_answer(self, query, context):
        """
        Генерирует ответ с использованием Chain-of-Thought (CoT) через extractive QA
        """
        # Определяем тип вопроса
        question_type = self.prompt_manager.classify_query(query)

        # Генерируем промт с CoT как инструкцию для extractive QA
        cot_instruction = self.prompt_manager.generate_prompt(
            question_type=question_type,
            context=context,
            query=query
        )

        # Улучшаем контекст с инструкциями
        enhanced_context = f"""
        [ИНСТРУКЦИЯ]
        {cot_instruction}
        Найди в тексте ниже точный ответ на вопрос: "{query}".
        Если точного ответа нет, верни наиболее релевантный фрагмент.

        [КОНТЕКСТ]
        {context}
        [КОНЕЦ КОНТЕКСТА]
        """

        # Используем модель для extractive QA
        inputs = self.qa_tokenizer(
            query,
            enhanced_context,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.qa_model(**inputs)

        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits) + 1
        extracted_answer = self.qa_tokenizer.convert_tokens_to_string(
            self.qa_tokenizer.convert_ids_to_tokens(inputs.input_ids[0][answer_start:answer_end])
        )

        # Если ответ пустой или слишком короткий, используем fallback
        if not extracted_answer.strip() or len(extracted_answer.strip()) < 10:
            extracted_answer = self._generate_fallback_answer(query, context)

        # Добавляем стандартное завершение ответа
        if question_type != 'general':
            extracted_answer += "\n\nЕсли у вас остались вопросы, рекомендую уточнить детали у администратора клиники или вашего лечащего врача."

        return extracted_answer

    def _generate_fallback_answer(self, query, context):
        """Генерирует резервный ответ на основе типа вопроса"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['записаться', 'прием', 'регистратура']):
            return (
                "Записаться на прием к врачу можно несколькими способами:\n\n"
                "1. Через сайт клиники\n"
                "2. По телефону регистратуры\n"
                "3. Через мобильное приложение\n"
                "4. Лично в регистратуре\n\n"
                "Для записи потребуется паспорт и полис ОМС."
            )
        elif any(word in query_lower for word in ['документ', 'справка', 'полис']):
            return (
                "Для медицинских процедур обычно требуются:\n"
                "- Паспорт\n"
                "- Полис ОМС\n"
                "- СНИЛС (по желанию)\n"
                "- Направление от врача (для некоторых процедур)\n\n"
                "Уточните полный список в регистратуре вашей поликлиники."
            )
        else:
            return (
                "К сожалению, в нашей базе нет точного ответа на этот вопрос.\n"
                "Рекомендуем обратиться в регистратуру вашей поликлиники или к лечащему врачу."
            )



    def search_and_generate(self, query, k=5):
        results = self.search_qa(query, k)
        filtered_results = self.filter_relevant_results(query, results)
        context = "\n".join([f"Вопрос: {hit.entity.question}\nОтвет: {hit.entity.answer}" for hit in filtered_results])
        answer = self.generate_answer(query, context)
        return answer, filtered_results
