import json
from datetime import datetime
from auth.database import get_db
from auth.models import Resume, ResumeAnalysis

class ResumeService:
    """Сервис для работы с резюме"""
    
    def save_resume(self, user_id: int, filename: str, file_content: str, 
                   file_type: str, file_size: int, original_text: str = None):
        """Сохранение резюме в базу данных"""
        db = get_db()
        try:
            resume = Resume(
                user_id=user_id,
                filename=filename,
                file_content=file_content,
                file_type=file_type,
                file_size=file_size,
                original_text=original_text or file_content,
                upload_date=datetime.now()
            )
            
            db.add(resume)
            db.commit()
            db.refresh(resume)
            return resume.id
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def save_resume_analysis(self, resume_id: int, user_id: int, analysis_data: dict):
        """Сохранение анализа резюме"""
        db = get_db()
        try:
            analysis = ResumeAnalysis(
                resume_id=resume_id,
                user_id=user_id,
                authenticity_score=analysis_data.get('score', 0),
                detected_position=analysis_data.get('detected_position', 'Не определено'),
                flags=json.dumps(analysis_data.get('flags', [])),
                recommendations=json.dumps(analysis_data.get('recommendations', [])),
                verdict=analysis_data.get('verdict', 'Не проверено'),
                analysis_data=json.dumps(analysis_data),
                created_at=datetime.now()
            )
            
            db.add(analysis)
            
            # Обновляем статус резюме
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                resume.is_analyzed = True
                resume.analysis_date = datetime.now()
                resume.detected_position = analysis_data.get('detected_position')
                resume.experience_level = analysis_data.get('experience_level', 'Не определен')
                resume.skills = json.dumps(analysis_data.get('detected_skills', []))
            
            db.commit()
            return analysis.id
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_user_resumes(self, user_id: int):
        """Получение всех резюме пользователя"""
        db = get_db()
        try:
            return db.query(Resume).filter(
                Resume.user_id == user_id
            ).order_by(Resume.upload_date.desc()).all()
        finally:
            db.close()
    
    def get_resume_analyses(self, user_id: int):
        """Получение анализов резюме пользователя"""
        db = get_db()
        try:
            return db.query(ResumeAnalysis).filter(
                ResumeAnalysis.user_id == user_id
            ).order_by(ResumeAnalysis.created_at.desc()).all()
        finally:
            db.close()
    
    def get_all_resumes(self):
        """Получение всех резюме (для HR)"""
        db = get_db()
        try:
            return db.query(Resume).filter(
                Resume.is_analyzed == True
            ).order_by(Resume.upload_date.desc()).all()
        finally:
            db.close()