import random
from datetime import datetime

class ResumeAnalyzer:
    """Анализатор резюме"""
    
    def __init__(self):
        self.position_keywords = {
            "разработчик": "Разработчик",
            "программист": "Разработчик", 
            "developer": "Разработчик",
            "менеджер": "Менеджер",
            "manager": "Менеджер",
            "аналитик": "Аналитик",
            "analyst": "Аналитик",
            "дизайнер": "Дизайнер",
            "designer": "Дизайнер",
            "маркетинг": "Маркетолог",
            "marketing": "Маркетолог",
            "продаж": "Менеджер по продажам",
            "sales": "Менеджер по продажам"
        }
        
        self.skill_keywords = {
            "python": "Python", "java": "Java", "javascript": "JavaScript",
            "sql": "SQL", "html": "HTML", "css": "CSS", "react": "React",
            "vue": "Vue.js", "angular": "Angular", "docker": "Docker",
            "git": "Git", "linux": "Linux"
        }
    
    def analyze_resume(self, resume_text: str, filename: str = None):
        """Анализ резюме"""
        try:
            detected_position = self._detect_position(resume_text)
            detected_skills = self._detect_skills(resume_text)
            experience_level = self._detect_experience_level(resume_text)
            
            authenticity_score = self._calculate_authenticity_score(resume_text)
            flags = self._analyze_issues(resume_text)
            recommendations = self._generate_recommendations(flags)
            
            return {
                "score": authenticity_score,
                "flags": flags,
                "recommendations": recommendations,
                "verdict": "Достоверно" if authenticity_score >= 80 else "Требует проверки",
                "detected_position": detected_position,
                "detected_skills": detected_skills,
                "experience_level": experience_level,
                "analysis_date": str(datetime.now()),
                "filename": filename
            }
            
        except Exception as e:
            return {
                "score": 50,
                "flags": ["Ошибка анализа резюме"],
                "recommendations": ["Попробуйте загрузить резюме в другом формате"],
                "verdict": "Ошибка анализа",
                "detected_position": "Не определено",
                "detected_skills": [],
                "experience_level": "Не определен",
                "analysis_date": str(datetime.now()),
                "filename": filename
            }
    
    def _detect_position(self, text: str) -> str:
        """Определение позиции из текста резюме"""
        text_lower = text.lower()
        for keyword, position in self.position_keywords.items():
            if keyword in text_lower:
                return position
        return "Специалист"
    
    def _detect_skills(self, text: str) -> list:
        """Определение навыков из текста резюме"""
        text_lower = text.lower()
        skills = []
        for keyword, skill in self.skill_keywords.items():
            if keyword in text_lower:
                skills.append(skill)
        return skills[:10]
    
    def _detect_experience_level(self, text: str) -> str:
        """Определение уровня опыта"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["senior", "ведущий", "руковод", "team lead"]):
            return "Senior"
        elif any(word in text_lower for word in ["middle", "опыт 3", "опыт 4", "опыт 5"]):
            return "Middle"
        elif any(word in text_lower for word in ["junior", "начинающий", "стажер", "студент"]):
            return "Junior"
        else:
            return "Не определен"
    
    def _calculate_authenticity_score(self, text: str) -> float:
        """Расчет оценки достоверности"""
        score = 70
        
        if len(text) > 500:
            score += 10
        if "опыт работы" in text.lower():
            score += 5
        if "образование" in text.lower():
            score += 5
        if "навыки" in text.lower() or "skills" in text.lower():
            score += 5
        
        score += random.randint(-5, 10)
        return min(max(score, 50), 95)
    
    def _analyze_issues(self, text: str) -> list:
        """Анализ проблем в резюме"""
        issues = []
        
        if len(text) < 300:
            issues.append("Слишком краткое резюме")
        if "опыт работы" not in text.lower():
            issues.append("Отсутствует раздел с опытом работы")
        if "образование" not in text.lower():
            issues.append("Отсутствует раздел с образованием")
        
        if not issues:
            issues.append("Основные разделы присутствуют")
        
        return issues
    
    def _generate_recommendations(self, issues: list) -> list:
        """Генерация рекомендаций по улучшению"""
        recommendations_map = {
            "Слишком краткое резюме": "Добавьте больше деталей о проектах и достижениях",
            "Отсутствует раздел с опытом работы": "Добавьте подробное описание опыта работы",
            "Отсутствует раздел с образованием": "Укажите информацию об образовании"
        }
        
        recommendations = []
        for issue in issues:
            if issue in recommendations_map:
                recommendations.append(recommendations_map[issue])
        
        if not recommendations:
            recommendations = [
                "Рекомендуем добавить конкретные цифры и метрики",
                "Уточните сроки работы в каждом месте",
                "Добавьте информацию о реальных проектах и достижениях"
            ]
        
        return recommendations