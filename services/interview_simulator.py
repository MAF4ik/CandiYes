from typing import List, Dict
from utils.config import config

class InterviewSimulator:
    """Симулятор собеседования с кандидатом"""
    
    def __init__(self):
        self.client = None
        if config.OPENAI_API_KEY and config.OPENAI_API_KEY != "demo-mode":
            try:
                import openai
                self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            except ImportError:
                print("OpenAI не установлен, используем демо-режим")
        self.conversation_history = []
    
    def start_interview(self, candidate_profile: str, position: str) -> str:
        """Начало интервью"""
        if not self.client or config.OPENAI_API_KEY == "demo-mode":
            return "Здравствуйте! Расскажите, пожалуйста, о вашем опыте работы и почему вы заинтересованы в этой позиции?"
        
        # Здесь будет логика с OpenAI
        return "Здравствуйте! Расскажите о вашем профессиональном опыте."
    
    def ask_question(self, question: str) -> str:
        """Ответ на вопрос интервьюера"""
        if not self.client or config.OPENAI_API_KEY == "demo-mode":
            return "Это интересный вопрос. На основе моего опыта, я бы сказал, что..."
        
        # Здесь будет логика с OpenAI
        return "Спасибо за вопрос. Я думаю, что..."
    
    def generate_followup_question(self, user_answer: str, interview_type: str, position: str) -> str:
        """Генерация следующего вопроса для собеседования"""
        if not self.client or config.OPENAI_API_KEY == "demo-mode":
            questions = {
                "Техническое собеседование (IT)": "Расскажите о вашем опыте работы с базами данных?",
                "Собеседование на менеджера": "Как вы мотивируете команду на достижение целей?",
                "Behavioral интервью": "Приведите пример сложной ситуации и как вы с ней справились?",
                "Собеседование на стажировку": "Какие навыки вы хотите развить во время стажировки?"
            }
            return questions.get(interview_type, "Расскажите подробнее о вашем опыте?")
        
        # Здесь будет логика с OpenAI
        return "Расскажите подробнее о вашем опыте в этой области?"