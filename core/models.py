from typing import Dict, List, Optional
from pydantic import BaseModel

class CandidateAnalysis(BaseModel):
    candidate_id: str
    vacancy: str
    summary_score: float
    match_reasoning: str
    strengths: List[str]
    risks: List[str]
    competency_scores: Dict[str, float]
    interview_questions: List[str]
    salary_expectations: str
    availability: str
    key_experience: List[str]
    recommendation: str  # "hire", "consider", "reject"
    
    # Новые поля для анализа соискателей
    improvement_suggestions: List[str] = []
    strong_skills: List[str] = []
    match_score: float = 0.0
    recommended_courses: str = ""
    experience_level: str = ""
    
    def get_recommendation_display(self) -> str:
        recommendation_map = {
            "hire": "Пригласить на интервью",
            "consider": "Рассмотреть дополнительно", 
            "review": "Требуется проверка",
            "reject": "Отклонить"
        }
        return recommendation_map.get(self.recommendation, "Требуется оценка")

class BusinessMetrics(BaseModel):
    time_saved_minutes: int
    cost_savings: float  
    quality_improvement: float
    hiring_speed_days: int