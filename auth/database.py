from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import sqlite3
import hashlib

# Создаем папку data если ее нет
os.makedirs('data', exist_ok=True)

# SQLite база данных
SQLALCHEMY_DATABASE_URL = "sqlite:///data/database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def init_db():
    from auth.models import Base
    Base.metadata.create_all(bind=engine)
    
    # Создаем тестовых пользователей
    db = SessionLocal()
    try:
        from auth.models import User
        
        # Проверяем, есть ли уже пользователи
        if not db.query(User).first():
            # Создаем тестового HR
            hr_user = User(
                email="hr@company.com",
                username="hr_manager",
                hashed_password=hashlib.sha256("hr123".encode()).hexdigest(),
                full_name="HR Менеджер",
                user_type="hr",
                company="ТехноКорп",
                position="HR Manager"
            )
            
            # Создаем тестового соискателя
            candidate_user = User(
                email="candidate@example.com",
                username="candidate",
                hashed_password=hashlib.sha256("candidate123".encode()).hexdigest(),
                full_name="Иван Иванов",
                user_type="candidate",
                phone="+79991234567",
                location="Москва"
            )
            
            db.add(hr_user)
            db.add(candidate_user)
            db.commit()
            print("✅ Тестовые пользователи созданы!")
            
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых пользователей: {e}")
    finally:
        db.close()

# Инициализация базы при импорте
init_db()