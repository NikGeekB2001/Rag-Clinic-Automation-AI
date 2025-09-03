import os
import pandas as pd
from typing import List, Dict
from dotenv import load_dotenv
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline

# Загрузка переменных окружения
load_dotenv()

# Данные
documents_data = [
    {
        "id": 1,
        "question": "Как записаться на прием к врачу?",
        "answer": """Записаться на прием к врачу можно несколькими способами:
1) Через сайт клиники: выберите врача, дату и время приема, заполните форму записи.
2) По телефону: позвоните в регистратуру клиники и запишитесь на удобное время.
3) Через мобильное приложение клиники: выберите врача и запишитесь на прием.
4) Лично в регистратуре клиники.
Для записи может потребоваться полис ОМС или данные страховки, если вы записываетесь по ДМС.""",
        "url": "clinic/appointment"
    },
    # Добавьте остальные вопросы и ответы
]

# Создание DataFrame
df = pd.DataFrame(documents_data)

# Загрузка данных в LangChain
loader = DataFrameLoader(df, page_content_column='question')
documents = loader.load()

# Разделение текста на части
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

# Векторизация с использованием HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Создание хранилища FAISS
db = FAISS.from_documents(texts, embeddings)

# Загрузка модели и токенайзера
model_name = "Den4ikAI/rubert_large_squad_2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

# Создание пайплайна для вопросно-ответной системы
qa_pipeline = pipeline(
    "question-answering",
    model=model,
    tokenizer=tokenizer,
    device=-1  # Используем CPU
)

# Запрос
query = 'Как записаться на прием к врачу?'

# Получение релевантных документов
retriever = db.as_retriever()
docs = retriever.invoke(query)

# Формирование контекста
context = "\n".join([doc.page_content + "\n" + doc.metadata['answer'] for doc in docs])

# Задаем вопрос и контекст в нужном формате
question_answering_input = {
    "question": query,
    "context": context
}

# Получение ответа от модели
response = qa_pipeline(question_answering_input)

print(response)
