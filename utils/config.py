import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация приложения"""
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "demo-mode")
    
    # Фреймворк компетенций для разных вакансий
    COMPETENCY_FRAMEWORK = {
        "Frontend разработчик": {
            "hard_skills": ["JavaScript", "React", "HTML/CSS", "TypeScript"],
            "soft_skills": ["Адаптивность", "Внимание к деталям", "Коммуникация"],
            "key_indicators": ["Качество кода", "Производительность", "UX/UI понимание"]
        },
        "Backend разработчик": {
            "hard_skills": ["Python", "Django", "SQL", "Docker"],
            "soft_skills": ["Аналитическое мышление", "Решение проблем", "Работа в команде"],
            "key_indicators": ["Архитектура", "Безопасность", "Масштабируемость"]
        },
        "Data Scientist": {
            "hard_skills": ["Python", "ML", "SQL", "Pandas"],
            "soft_skills": ["Аналитическое мышление", "Критическое мышление", "Визуализация"],
            "key_indicators": ["Точность моделей", "Анализ данных", "Бизнес-инсайты"]
        },
        "Project Manager": {
            "hard_skills": ["Agile", "Jira", "Управление проектами", "Бюджетирование"],
            "soft_skills": ["Лидерство", "Коммуникация", "Тайм-менеджмент"],
            "key_indicators": ["Своевременность", "Бюджет", "Качество"]
        },
        "UX/UI дизайнер": {
            "hard_skills": ["Figma", "Adobe XD", "Прототипирование", "Research"],
            "soft_skills": ["Креативность", "Эмпатия", "Коммуникация"],
            "key_indicators": ["Usability", "Визуальная привлекательность", "User satisfaction"]
        },
        "Менеджер по продажам": {
            "hard_skills": ["CRM", "Переговоры", "Анализ рынка", "Презентации"],
            "soft_skills": ["Коммуникация", "Убеждение", "Стрессоустойчивость"],
            "key_indicators": ["Конверсия", "Выручка", "Лояльность клиентов"]
        }
    }

config = Config()