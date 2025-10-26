from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    user_type = Column(String(20), nullable=False)  # 'candidate' or 'hr'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
    
    # Для HR специалистов
    company = Column(String(100))
    position = Column(String(100))
    
    # Для соискателей
    phone = Column(String(20))
    location = Column(String(100))

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    filename = Column(String(255))
    file_content = Column(Text)
    file_type = Column(String(10))
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=func.now())
    original_text = Column(Text)
    
    # Анализ резюме
    detected_position = Column(String(100))
    experience_level = Column(String(50))
    skills = Column(JSON)
    
    # Статус анализа
    is_analyzed = Column(Boolean, default=False)
    analysis_date = Column(DateTime)

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    
    # Результаты анализа
    authenticity_score = Column(Float)
    detected_position = Column(String(100))
    flags = Column(JSON)
    recommendations = Column(JSON)
    verdict = Column(String(50))
    analysis_data = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())