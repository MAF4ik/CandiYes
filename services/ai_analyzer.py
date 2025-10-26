from typing import Dict, List
from core.models import CandidateAnalysis
from utils.config import config

class AIAnalyzer:
    """Класс для AI-анализа кандидатов"""
    
    def __init__(self):
        # Отложенная инициализация клиента OpenAI
        self.client = None
        if config.OPENAI_API_KEY and config.OPENAI_API_KEY != "demo-mode":
            try:
                import openai
                self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            except ImportError:
                print("OpenAI не установлен, используем демо-режим")
    
    def analyze_candidate(self, resume_text: str, vacancy: str, requirements: str) -> CandidateAnalysis:
        """Анализ кандидата на основе резюме и требований вакансии"""
        
        # Для демо-режима возвращаем mock данные
        if not self.client or config.OPENAI_API_KEY == "demo-mode":
            return self._get_mock_analysis(vacancy)
        
        try:
            # Здесь будет реальный вызов OpenAI API
            # Пока возвращаем mock данные
            return self._get_mock_analysis(vacancy)
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return self._get_mock_analysis(vacancy)
    
    def _get_mock_analysis(self, vacancy: str) -> CandidateAnalysis:
        """Возвращает mock-анализ для демо"""
        import uuid
        
        return CandidateAnalysis(
            candidate_id=str(uuid.uuid4()),
            vacancy=vacancy,
            summary_score=8.2,
            match_reasoning="Кандидат имеет релевантный опыт и навыки для позиции",
            strengths=[
                "Опыт работы в аналогичной должности 2+ года",
                "Хорошие технические навыки",
                "Коммуникативные способности"
            ],
            risks=[
                "Ограниченный опыт руководства",
                "Требуется развитие навыков презентации"
            ],
            competency_scores={
                "Опыт": 8.5,
                "Навыки": 7.8,
                "Мотивация": 8.0,
                "Стабильность": 7.5,
                "Образование": 8.0
            },
            interview_questions=[
                "Расскажите о вашем самом сложном проекте?",
                "Как вы решаете конфликты в команде?",
                "Какие технологии вы планируете изучать?",
                "Почему вы хотите работать в нашей компании?",
                "Как вы оцениваете свой уровень владения Python?"
            ],
            salary_expectations="120 000 - 150 000 руб",
            availability="2 недели",
            key_experience=[
                "Разработка веб-приложений на Python",
                "Работа с базами данных SQL",
                "Участие в agile-проектах"
            ],
            recommendation="consider",
            improvement_suggestions=[
                "Добавить больше деталей о проектах",
                "Указать конкретные достижения",
                "Опишите ваш вклад в командные успехи"
            ],
            strong_skills=["Python", "Django", "SQL", "Git"],
            match_score=82.0,
            recommended_courses="Курсы по продвинутому Python и управлению проектами",
            experience_level="Middle"
        )