from langchain.prompts import PromptTemplate

class MedicalPromptManager:
    """
    Класс для управления медицинскими промтами с использованием Chain-of-Thought (CoT)
    """

    def __init__(self):
        self.prompts = self._initialize_prompts()

    def _initialize_prompts(self):
        """Инициализация всех промтов с CoT"""

        # Основной промт с Chain-of-Thought
        cot_template = """
        Ты опытный медицинский специалист с 15-летним стажем работы в поликлинике.
        Ответь на вопрос пациента, следуя пошаговому рассуждению (Chain-of-Thought).

        КОНТЕКСТ (информация из базы знаний):
        {context}

        ВОПРОС ПАЦИЕНТА: {query}

        РАССУЖДЕНИЕ:
        1. Анализ вопроса:
           - Определи тип вопроса: {question_type}
           - Ключевые слова: {keywords}
           - Что именно спрашивает пациент?

        2. Поиск релевантной информации:
           - Какие данные из контекста могут помочь ответить?
           - Есть ли в контексте прямые ответы на вопрос?
           - Релевантные части контекста:
             {relevant_context}

        3. Формулировка ответа:
           - Как лучше структурировать ответ?
           - Нужно ли использовать списки, таблицы или простой текст?
           - Какие дополнительные детали будут полезны пациенту?

        4. Проверка и рекомендации:
           - Достаточно ли информации для полного ответа?
           - Какие дополнительные рекомендации можно дать?
           - Нужно ли посоветовать пациенту уточнить что-то у врача?

        5. Итоговый ответ:
           - Сформулируй окончательный ответ на основе предыдущих шагов
           - Используй профессиональный, но доступный язык
           - Структурируй ответ для лучшего восприятия

        ОТВЕТ ВРАЧА:
        """

        # Специализированные инструкции для разных типов вопросов
        prompt_instructions = {
            'appointment': """
            Дай подробную инструкцию о том, как записаться на прием к врачу.
            Укажи все возможные способы записи и необходимые документы.
            """,

            'documents': """
            Составь полный список документов, необходимых для медицинских процедур.
            Объясни, для чего нужен каждый документ.
            """,

            'tests': """
            Перечисли все необходимые анализы и исследования.
            Объясни, как к ним подготовиться и как получить результаты.
            """,

            'preparation': """
            Дай детальные рекомендации по подготовке к медицинским процедурам.
            Укажи все ограничения и требования.
            """,

            'general': """
            Ответь на вопрос пациента, используя информацию из контекста.
            Если информации недостаточно, уточни, что нужно сделать для получения точного ответа.
            """
        }

        # Создаем промты для каждого типа вопросов
        prompts = {}
        for question_type, instructions in prompt_instructions.items():
            prompts[question_type] = PromptTemplate(
                template=cot_template,
                input_variables=["context", "query", "question_type", "keywords", "relevant_context"]
            )


        return prompts

    def classify_query(self, query):
        """Определяет тип вопроса для выбора подходящего промта"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['записаться', 'запись', 'прием', 'приём', 'врач', 'специалист']):
            return 'appointment'
        elif any(word in query_lower for word in ['документ', 'справка', 'полис', 'паспорт', 'снилс']):
            return 'documents'
        elif any(word in query_lower for word in ['анализ', 'тест', 'исследование', 'диабет', 'глюкоза', 'кровь', 'моча']):
            return 'tests'
        elif any(word in query_lower for word in ['подготовка', 'подготовиться', 'как подготовиться']):
            return 'preparation'
        else:
            return 'general'

    def extract_keywords(self, query):
        """Извлекает ключевые слова из запроса"""
        stop_words = {'как', 'что', 'где', 'когда', 'нужно', 'можно', 'надо', 'нужны', 'какие', 'какой'}
        words = [word.strip("?,!.") for word in query.lower().split()]
        return [word for word in words if word not in stop_words and len(word) > 3]

    def extract_relevant_context(self, query_keywords, context):
        """Извлекает релевантные части контекста"""
        relevant_lines = []
        for line in context.split('\\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in query_keywords):
                relevant_lines.append(f"- {line}")

        if not relevant_lines:
            return ["Релевантная информация в контексте не найдена."]
        else:
            return relevant_lines

    def generate_prompt(self, question_type, context, query):
        """Генерирует финальный промт с CoT"""
        keywords = self.extract_keywords(query)
        relevant_context = '\\n'.join(self.extract_relevant_context(keywords, context))

        prompt = self.prompts[question_type]
        return prompt.format(
            context=context,
            query=query,
            question_type=question_type,
            keywords=', '.join(keywords),
            relevant_context=relevant_context
        )
