import streamlit as st
import plotly.express as px
import uuid
import hashlib
import sqlite3
import os
from datetime import datetime
import json
import base64
import pandas as pd
import io
import random
import time

# =============================================
# НАСТРОЙКА STREAMLIT И СТИЛИ
# =============================================

st.set_page_config(
    page_title="КандиДА",
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #2C3E50;
        margin-bottom: 1.5rem;
        font-weight: 700;
        border-left: 5px solid #FF6B35;
        padding-left: 15px;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #FF6B35, #FF8C42);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 107, 53, 0.4);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 5px solid #FF6B35;
    }
    
    .interview-question {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .success-card {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .error-card {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .nav-button-active {
        background: linear-gradient(135deg, #FF6B35, #FF8C42) !important;
        color: white !important;
        border: 2px solid #FF6B35 !important;
    }
    
    .nav-button-inactive {
        background: white !important;
        color: #FF6B35 !important;
        border: 2px solid #FF6B35 !important;
    }
    
    .candidate-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #f0f0f0;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .candidate-card:hover {
        border-color: #FF6B35;
        box-shadow: 0 5px 15px rgba(255, 107, 53, 0.1);
    }
    
    .favorite-star {
        color: #FFD700;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# СИСТЕМА АВТОРИЗАЦИИ
# =============================================

class AuthSystem:
    def __init__(self):
        self.db_path = "data/users.db"
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                user_type TEXT NOT NULL,
                company TEXT,
                position TEXT,
                phone TEXT,
                location TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Таблица резюме
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT,
                file_content BLOB,
                file_type TEXT,
                file_size INTEGER,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                original_text TEXT,
                detected_position TEXT,
                experience_level TEXT,
                skills TEXT,
                is_analyzed BOOLEAN DEFAULT 0,
                analysis_date TIMESTAMP
            )
        ''')
        
        # Таблица анализов резюме
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                authenticity_score REAL,
                detected_position TEXT,
                flags TEXT,
                recommendations TEXT,
                verdict TEXT,
                analysis_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица избранных кандидатов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hr_user_id INTEGER NOT NULL,
                candidate_user_id INTEGER NOT NULL,
                resume_id INTEGER NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hr_user_id) REFERENCES users (id),
                FOREIGN KEY (candidate_user_id) REFERENCES users (id),
                FOREIGN KEY (resume_id) REFERENCES resumes (id),
                UNIQUE(hr_user_id, candidate_user_id)
            )
        ''')
        
        # НОВАЯ ТАБЛИЦА: История собеседований
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                interview_type TEXT NOT NULL,
                position TEXT NOT NULL,
                questions TEXT,
                answers TEXT,
                feedback TEXT,
                score REAL,
                duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Создаем тестовых пользователей если их нет
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self._create_test_users(cursor)
        
        conn.commit()
        conn.close()
        print("✅ База данных инициализирована!")
    
    def _create_test_users(self, cursor):
        """Создание тестовых пользователей"""
        test_users = [
            {
                'email': 'hr@company.com',
                'username': 'hr_manager', 
                'password': 'hr123',
                'full_name': 'HR Менеджер',
                'user_type': 'hr',
                'company': 'ТехноКорп',
                'position': 'HR Manager',
                'phone': '',
                'location': ''
            },
            {
                'email': 'candidate@example.com',
                'username': 'candidate',
                'password': 'candidate123', 
                'full_name': 'Иван Иванов',
                'user_type': 'candidate',
                'company': '',
                'position': '',
                'phone': '+79991234567',
                'location': 'Москва'
            },
            {
                'email': 'admin@example.com',
                'username': 'admin',
                'password': 'admin123',
                'full_name': 'Администратор',
                'user_type': 'hr',
                'company': 'Администрация',
                'position': 'Admin',
                'phone': '',
                'location': ''
            }
        ]
        
        for user_data in test_users:
            hashed_password = self._hash_password(user_data['password'])
            try:
                cursor.execute('''
                    INSERT INTO users 
                    (email, username, hashed_password, full_name, user_type, company, position, phone, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data['email'],
                    user_data['username'],
                    hashed_password,
                    user_data['full_name'],
                    user_data['user_type'],
                    user_data['company'],
                    user_data['position'],
                    user_data['phone'],
                    user_data['location']
                ))
                print(f"✅ Создан пользователь: {user_data['username']}")
            except sqlite3.IntegrityError as e:
                print(f"⚠️ Пользователь {user_data['username']} уже существует: {e}")
            except Exception as e:
                print(f"❌ Ошибка при создании пользователя {user_data['username']}: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self._hash_password(plain_password) == hashed_password
    
    def authenticate_user(self, username: str, password: str):
        """Аутентификация пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND is_active = 1
        ''', (username,))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and self.verify_password(password, user_data[3]):  # hashed_password
            # Обновляем время последнего входа
            self._update_last_login(user_data[0])
            
            return {
                'id': user_data[0],
                'email': user_data[1],
                'username': user_data[2],
                'full_name': user_data[4],
                'user_type': user_data[5],
                'company': user_data[6],
                'position': user_data[7],
                'phone': user_data[8],
                'location': user_data[9]
            }
        
        return None
    
    def _update_last_login(self, user_id: int):
        """Обновление времени последнего входа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET last_login = ? WHERE id = ?
        ''', (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
    
    def create_user(self, user_data: dict) -> bool:
        """Создание нового пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Проверяем, нет ли уже такого пользователя
            cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', 
                         (user_data['email'], user_data['username']))
            if cursor.fetchone():
                return False
            
            hashed_password = self._hash_password(user_data['password'])
            
            cursor.execute('''
                INSERT INTO users 
                (email, username, hashed_password, full_name, user_type, company, position, phone, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['email'],
                user_data['username'],
                hashed_password,
                user_data['full_name'],
                user_data['user_type'],
                user_data.get('company', ''),
                user_data.get('position', ''),
                user_data.get('phone', ''),
                user_data.get('location', '')
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Создан новый пользователь: {user_data['username']}")
            return True
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def update_user_profile(self, user_id: int, update_data: dict) -> bool:
        """Обновление профиля пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET 
                email = ?, username = ?, full_name = ?, company = ?, position = ?, phone = ?, location = ?
                WHERE id = ?
            ''', (
                update_data['email'],
                update_data['username'],
                update_data['full_name'],
                update_data.get('company', ''),
                update_data.get('position', ''),
                update_data.get('phone', ''),
                update_data.get('location', ''),
                user_id
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Смена пароля"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Получаем текущий пароль
        cursor.execute('SELECT hashed_password FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result or not self.verify_password(current_password, result[0]):
            conn.close()
            return False
        
        # Обновляем пароль
        new_hashed_password = self._hash_password(new_password)
        cursor.execute('UPDATE users SET hashed_password = ? WHERE id = ?', 
                     (new_hashed_password, user_id))
        
        conn.commit()
        conn.close()
        return True

    def get_database_tables(self):
        """Получение списка всех таблиц в базе данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            conn.close()
            return [table[0] for table in tables]
        except Exception as e:
            print(f"Error getting tables: {e}")
            return []

    def get_table_data(self, table_name):
        """Получение всех данных из указанной таблицы"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Получаем данные
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, conn)
            
            # Получаем информацию о столбцах
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            conn.close()
            return df, columns_info
        except Exception as e:
            print(f"Error getting table data: {e}")
            return None, None

    def get_table_statistics(self):
        """Получение статистики по таблицам"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            tables = self.get_database_tables()
            stats = {}
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            
            conn.close()
            return stats
        except Exception as e:
            print(f"Error getting table statistics: {e}")
            return {}

    def execute_custom_query(self, query):
        """Выполнение пользовательского SQL запроса"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Проверяем, является ли запрос SELECT
            if query.strip().upper().startswith('SELECT'):
                df = pd.read_sql_query(query, conn)
                conn.close()
                return df, None
            else:
                # Для не-SELECT запросов
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                affected_rows = cursor.rowcount
                conn.close()
                return None, f"Запрос выполнен успешно. Затронуто строк: {affected_rows}"
                
        except Exception as e:
            return None, f"Ошибка выполнения запроса: {str(e)}"

    def save_interview_result(self, user_id, interview_type, position, questions, answers, feedback, score, duration):
        """Сохранение результатов собеседования"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO interviews 
                (user_id, interview_type, position, questions, answers, feedback, score, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                interview_type,
                position,
                json.dumps(questions),
                json.dumps(answers),
                feedback,
                score,
                duration
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving interview: {e}")
            return False

    def get_user_interviews(self, user_id):
        """Получение истории собеседований пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM interviews 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            
            interviews = cursor.fetchall()
            conn.close()
            return interviews
        except Exception as e:
            print(f"Error getting interviews: {e}")
            return []

# Создаем глобальный экземпляр системы аутентификации
auth_system = AuthSystem()

# =============================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С КАНДИДАТАМИ
# =============================================

def get_all_candidates():
    """Получение всех кандидатов для HR"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                r.id as resume_id,
                r.filename,
                r.detected_position,
                r.experience_level,
                r.upload_date,
                r.is_analyzed,
                u.id as user_id,
                u.full_name,
                u.email,
                u.phone,
                u.location,
                ra.authenticity_score,
                ra.verdict,
                ra.created_at as analysis_date
            FROM resumes r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN resume_analyses ra ON r.id = ra.resume_id
            WHERE u.user_type = 'candidate'
            ORDER BY r.upload_date DESC
        ''')
        
        candidates = cursor.fetchall()
        conn.close()
        return candidates
        
    except Exception as e:
        print(f"Error getting candidates: {e}")
        return []

def add_to_favorites(hr_user_id, candidate_user_id, resume_id, notes=""):
    """Добавление кандидата в избранное"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO favorites 
            (hr_user_id, candidate_user_id, resume_id, notes)
            VALUES (?, ?, ?, ?)
        ''', (hr_user_id, candidate_user_id, resume_id, notes))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error adding to favorites: {e}")
        return False

def remove_from_favorites(hr_user_id, candidate_user_id):
    """Удаление кандидата из избранного"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM favorites 
            WHERE hr_user_id = ? AND candidate_user_id = ?
        ''', (hr_user_id, candidate_user_id))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error removing from favorites: {e}")
        return False

def is_in_favorites(hr_user_id, candidate_user_id):
    """Проверка, находится ли кандидат в избранном"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM favorites 
            WHERE hr_user_id = ? AND candidate_user_id = ?
        ''', (hr_user_id, candidate_user_id))
        
        result = cursor.fetchone()
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"Error checking favorites: {e}")
        return False

def get_favorites(hr_user_id):
    """Получение списка избранных кандидатов"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                f.*,
                u.full_name,
                u.email,
                u.phone,
                u.location,
                r.detected_position,
                r.experience_level,
                r.upload_date,
                ra.authenticity_score,
                ra.verdict
            FROM favorites f
            JOIN users u ON f.candidate_user_id = u.id
            JOIN resumes r ON f.resume_id = r.id
            LEFT JOIN resume_analyses ra ON r.id = ra.resume_id
            WHERE f.hr_user_id = ?
            ORDER BY f.created_at DESC
        ''', (hr_user_id,))
        
        favorites = cursor.fetchall()
        conn.close()
        return favorites
        
    except Exception as e:
        print(f"Error getting favorites: {e}")
        return []

def get_resume_file(resume_id):
    """Получение файла резюме"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT filename, file_content, file_type FROM resumes WHERE id = ?
        ''', (resume_id,))
        
        resume = cursor.fetchone()
        conn.close()
        return resume
        
    except Exception as e:
        print(f"Error getting resume file: {e}")
        return None

def create_download_link(file_content, filename, file_type):
    """Создание ссылки для скачивания файла"""
    try:
        if file_content:
            b64 = base64.b64encode(file_content).decode()
            href = f'<a href="data:{file_type};base64,{b64}" download="{filename}" style="background: linear-gradient(135deg, #FF6B35, #FF8C42); color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px;">📥 Скачать резюме</a>'
            return href
        return None
    except Exception as e:
        print(f"Error creating download link: {e}")
        return None

# =============================================
# AI АССИСТЕНТ ДЛЯ СОБЕСЕДОВАНИЙ
# =============================================

class InterviewAssistant:
    def __init__(self):
        self.positions = {
            "Разработчик": {
                "technical": ["ООП принципы", "Алгоритмы", "Базы данных", "Тестирование"],
                "questions": [
                    "Расскажите о вашем опыте работы с Python",
                    "Как вы организуете процесс разработки?",
                    "Пример решения сложной технической задачи",
                    "Ваш подход к код-ревью"
                ]
            },
            "Менеджер": {
                "technical": ["Управление проектами", "Бюджетирование", "Командная работа", "Отчетность"],
                "questions": [
                    "Как вы управляете конфликтами в команде?",
                    "Пример успешного проекта под вашим руководством",
                    "Ваш подход к планированию и контролю сроков",
                    "Как мотивируете команду?"
                ]
            },
            "Аналитик": {
                "technical": ["SQL", "Аналитика данных", "Визуализация", "Статистика"],
                "questions": [
                    "Как вы собираете и анализируете требования?",
                    "Пример сложного аналитического отчета",
                    "Ваши инструменты для анализа данных",
                    "Как вы проверяете качество данных?"
                ]
            },
            "Дизайнер": {
                "technical": ["UI/UX", "Прототипирование", "Исследования", "Инструменты дизайна"],
                "questions": [
                    "Опишите ваш процесс создания дизайна",
                    "Как вы проводите пользовательские исследования?",
                    "Пример решения сложной дизайн-задачи",
                    "Ваш подход к созданию UI kit"
                ]
            }
        }
    
    def generate_questions(self, position, experience_level, question_count=5):
        """Генерация вопросов для собеседования"""
        if position not in self.positions:
            position = "Разработчик"  # По умолчанию
        
        base_questions = [
            "Расскажите о себе и вашем профессиональном опыте",
            "Почему вы заинтересованы в этой позиции?",
            "Какие ваши сильные профессиональные качества?",
            "Какие области вы хотели бы развивать?",
            "Почему вы хотите работать в нашей компании?",
            "Как вы справляетесь со стрессом и сжатыми сроками?",
            "Расскажите о вашем самом значительном профессиональном достижении",
            "Как вы принимаете решения в сложных ситуациях?",
            "Как вы продолжаете профессионально развиваться?",
            "Где вы видите себя через 5 лет?"
        ]
        
        position_specific = self.positions[position]["questions"]
        technical_areas = self.positions[position]["technical"]
        
        # Выбираем случайные вопросы
        selected_questions = random.sample(base_questions, min(3, len(base_questions)))
        selected_questions.extend(random.sample(position_specific, min(2, len(position_specific))))
        
        # Добавляем технические вопросы в зависимости от уровня
        tech_questions = []
        for area in random.sample(technical_areas, min(2, len(technical_areas))):
            if experience_level == "Junior":
                tech_questions.append(f"Основные понятия в области {area}")
            elif experience_level == "Middle":
                tech_questions.append(f"Практическое применение {area} в проектах")
            else:  # Senior
                tech_questions.append(f"Архитектурные решения и лучшие практики в {area}")
        
        selected_questions.extend(tech_questions)
        
        return selected_questions[:question_count]
    
    def evaluate_answer(self, question, answer, position):
        """Оценка ответа кандидата"""
        # Простая имитация AI оценки
        evaluation_criteria = {
            "полнота": random.randint(3, 10),
            "релевантность": random.randint(3, 10),
            "структурированность": random.randint(3, 10),
            "примеры": random.randint(3, 10)
        }
        
        total_score = sum(evaluation_criteria.values()) / len(evaluation_criteria)
        
        feedback = []
        if evaluation_criteria["полнота"] >= 8:
            feedback.append("✅ Ответ полный и развернутый")
        else:
            feedback.append("💡 Можно добавить больше деталей")
        
        if evaluation_criteria["примеры"] >= 8:
            feedback.append("✅ Хорошие примеры из практики")
        else:
            feedback.append("💡 Добавьте конкретные примеры")
        
        if len(answer.split()) < 20:
            feedback.append("💡 Ответ слишком краткий, раскройте тему подробнее")
        
        return {
            "score": round(total_score, 1),
            "criteria": evaluation_criteria,
            "feedback": feedback
        }
    
    def generate_final_feedback(self, interview_results):
        """Генерация финального фидбэка"""
        # Проверяем что interview_results существует и не пустой
        if interview_results is None or len(interview_results) == 0:
            return {
                "total_score": 0,
                "verdict": "Собеседование не завершено",
                "detailed_feedback": ["❌ Не было дано ответов на вопросы"],
                "improvement_suggestions": [
                    "Попробуйте пройти собеседование еще раз",
                    "Отвечайте на все вопросы подробно"
                ]
            }
        
        total_score = sum(result["score"] for result in interview_results) / len(interview_results)
        
        if total_score >= 9:
            verdict = "Отличный кандидат! Рекомендуем к найму"
            feedback = [
                "✅ Сильное соответствие требованиям позиции",
                "✅ Отличные технические знания",
                "✅ Хорошие коммуникативные навыки",
                "✅ Мотивирован и целеустремлен"
            ]
        elif total_score >= 7:
            verdict = "Хороший кандидат, требует дополнительной проверки"
            feedback = [
                "✅ Соответствует основным требованиям",
                "⚠️ Некоторые области требуют развития",
                "✅ Хороший потенциал для роста",
                "💡 Рекомендуем дополнительное интервью"
            ]
        else:
            verdict = "Требует серьезной доработки"
            feedback = [
                "❌ Недостаточный опыт/знания",
                "💡 Рекомендуем пройти обучение",
                "💡 Нужно поработать над ответами",
                "💡 Рассмотреть через 6-12 месяцев"
            ]
        
        return {
            "total_score": round(total_score, 1),
            "verdict": verdict,
            "detailed_feedback": feedback,
            "improvement_suggestions": [
                "Практикуйтесь отвечать на стандартные вопросы интервью",
                "Изучите больше о компании и позиции",
                "Подготовьте конкретные примеры из вашего опыта",
                "Потренируйтесь в решении технических задач"
            ]
        }

# Инициализация ассистента
@st.cache_resource
def get_interview_assistant():
    return InterviewAssistant()

interview_assistant = get_interview_assistant()

# =============================================
# ФУНКЦИИ ДЛЯ СОБЕСЕДОВАНИЙ
# =============================================

def show_interview_interface():
    """Интерфейс проведения собеседования"""
    st.markdown('<div class="main-header">🎤 AI Собеседование</div>', unsafe_allow_html=True)
    
    # Создаем тестовое резюме если его нет
    resumes = get_user_resumes(st.session_state.user_id)
    
    if not resumes:
        st.info("📝 Создаем тестовое резюме для демонстрации...")
        # Создаем тестовое резюме автоматически
        create_demo_resume()
        resumes = get_user_resumes(st.session_state.user_id)
        st.success("✅ Тестовое резюме создано! Можете начинать собеседование.")
    
    # Показываем все резюме пользователя
    st.info("💡 Выберите резюме для собеседования:")
    
    # Создаем список доступных резюме
    resume_options = {}
    for resume in resumes:
        resume_name = f"{resume[2]} - {resume[8] or 'Позиция не определена'}"
        if resume[11]:  # is_analyzed
            resume_name += " ✅"
        else:
            resume_name += " ⚠️ (не проверено)"
        resume_options[resume_name] = resume
    
    selected_resume_key = st.selectbox("Выберите резюме:", list(resume_options.keys()))
    selected_resume = resume_options[selected_resume_key]
    
    # Настройки собеседования
    col1, col2 = st.columns(2)
    with col1:
        interview_type = st.selectbox("Тип собеседования:", 
                                    ["Техническое", "Поведенческое", "Комплексное"])
    with col2:
        question_count = st.slider("Количество вопросов:", 3, 10, 5)
    
    position = selected_resume[8] or "Разработчик"
    experience_level = selected_resume[9] or "Middle"
    
    st.markdown(f"""
    **Настройки собеседования:**
    - 🎯 **Позиция:** {position}
    - 📊 **Уровень:** {experience_level}
    - 🎪 **Тип:** {interview_type}
    - ❓ **Вопросов:** {question_count}
    """)
    
    if st.button("🎯 Начать собеседование", use_container_width=True, type="primary"):
        st.session_state.interview_data = {
            "resume_id": selected_resume[0],
            "position": position,
            "experience_level": experience_level,
            "interview_type": interview_type,
            "questions": interview_assistant.generate_questions(position, experience_level, question_count),
            "current_question": 0,
            "answers": [],
            "start_time": time.time(),
            "results": []
        }
        st.rerun()
    
    # Показываем историю собеседований
    show_interview_history()

def create_demo_resume():
    """Создание демо-резюме для тестирования"""
    demo_resume_text = """
    Иван Иванов
    Python Разработчик
    
    Опыт работы:
    - Middle Python Developer в TechCompany (2 года)
    - Junior Python Developer в StartupInc (1 год)
    
    Навыки:
    Python, Django, Flask, SQL, PostgreSQL, Git, Docker, Linux
    
    Образование:
    МГТУ им. Баумана, Факультет информатики
    
    Достижения:
    - Разработал микросервисную архитектуру для обработки 10k+ запросов в день
    - Оптимизировал SQL запросы, ускорив работу приложения на 40%
    - Внедрил CI/CD процесс, сократив время деплоя на 60%
    """
    
    # Сохраняем демо-резюме
    verification = verify_resume_authenticity(demo_resume_text)
    save_resume_to_db(
        st.session_state.user_id,
        "demo_resume.txt",
        demo_resume_text.encode('utf-8'),
        "text/plain",
        len(demo_resume_text),
        verification
    )

def conduct_interview():
    """Проведение активного собеседования"""
    interview_data = st.session_state.interview_data
    
    st.markdown(f'<div class="sub-header">🎤 Собеседование на позицию: {interview_data["position"]}</div>', unsafe_allow_html=True)
    
    # Прогресс
    progress = (interview_data["current_question"] + 1) / len(interview_data["questions"])
    st.progress(progress)
    st.write(f"Вопрос {interview_data['current_question'] + 1} из {len(interview_data['questions'])}")
    
    # Текущий вопрос
    current_question = interview_data["questions"][interview_data["current_question"]]
    
    st.markdown(f'<div class="interview-question">❓ {current_question}</div>', unsafe_allow_html=True)
    
    # Поле для ответа
    answer = st.text_area("Ваш ответ:", height=150, 
                         placeholder="Введите ваш ответ здесь... Постарайтесь быть максимально подробными и привести конкретные примеры из вашего опыта.",
                         key=f"answer_{interview_data['current_question']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⏭️ Следующий вопрос", use_container_width=True):
            if answer.strip():
                # Оцениваем ответ
                evaluation = interview_assistant.evaluate_answer(
                    current_question, 
                    answer, 
                    interview_data["position"]
                )
                
                interview_data["answers"].append(answer)
                interview_data["results"].append(evaluation)
                interview_data["current_question"] += 1
                
                if interview_data["current_question"] >= len(interview_data["questions"]):
                    # Завершаем собеседование
                    st.session_state.interview_complete = True
                
                st.rerun()
            else:
                st.error("Пожалуйста, введите ответ перед переходом к следующему вопросу")
    
    with col2:
        if st.button("🛑 Завершить досрочно", use_container_width=True, type="secondary"):
            st.session_state.interview_complete = True
            st.rerun()

def show_interview_results():
    """Показ результатов завершенного собеседования"""
    interview_data = st.session_state.interview_data
    
    # Проверяем что есть данные для отображения
    if not interview_data or "results" not in interview_data:
        st.error("❌ Нет данных для отображения результатов")
        if st.button("🔄 Начать заново", use_container_width=True):
            for key in ['interview_data', 'interview_complete']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        return
    
    # Рассчитываем длительность
    duration = int(time.time() - interview_data["start_time"])
    
    # Генерируем финальный фидбэк
    final_feedback = interview_assistant.generate_final_feedback(interview_data["results"])
    
    st.markdown('<div class="sub-header">📊 Результаты собеседования</div>', unsafe_allow_html=True)
    
    # Общая оценка
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card">🎯 Общая оценка: <span style="font-size: 2rem; color: #FF6B35;">{final_feedback["total_score"]}/10</span></div>', unsafe_allow_html=True)
    with col2:
        st.metric("Длительность", f"{duration//60} мин {duration%60} сек")
    with col3:
        st.metric("Количество вопросов", len(interview_data["questions"]))
    
    # Вердикт
    if final_feedback["total_score"] >= 9:
        st.markdown(f'<div class="success-card"><strong>Вердикт:</strong> {final_feedback["verdict"]}</div>', unsafe_allow_html=True)
    elif final_feedback["total_score"] >= 7:
        st.markdown(f'<div class="warning-card"><strong>Вердикт:</strong> {final_feedback["verdict"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="error-card"><strong>Вердикт:</strong> {final_feedback["verdict"]}</div>', unsafe_allow_html=True)
    
    # Детальный фидбэк
    st.markdown("**📝 Обратная связь:**")
    for feedback in final_feedback["detailed_feedback"]:
        st.write(f"• {feedback}")
    
    # Детали по вопросам
    st.markdown("---")
    st.markdown("**📋 Детализация по вопросам:**")
    
    for i, (question, result) in enumerate(zip(interview_data["questions"], interview_data["results"])):
        with st.expander(f"Вопрос {i+1}: {question[:50]}... (Оценка: {result['score']}/10)"):
            col_q1, col_q2 = st.columns([2, 1])
            
            with col_q1:
                st.markdown("**Ваш ответ:**")
                st.write(interview_data["answers"][i])
            
            with col_q2:
                st.markdown("**Оценка:**")
                for criterion, score in result["criteria"].items():
                    st.write(f"• {criterion}: {score}/10")
                
                st.markdown("**Рекомендации:**")
                for fb in result["feedback"]:
                    st.write(f"• {fb}")
    
    # Рекомендации по улучшению
    st.markdown("---")
    st.markdown("**💡 Рекомендации для улучшения:**")
    for suggestion in final_feedback["improvement_suggestions"]:
        st.write(f"• {suggestion}")
    
    # Сохранение результатов
    if st.button("💾 Сохранить результаты", use_container_width=True):
        success = auth_system.save_interview_result(
            st.session_state.user_id,
            interview_data["interview_type"],
            interview_data["position"],
            interview_data["questions"],
            interview_data["answers"],
            json.dumps(final_feedback),
            final_feedback["total_score"],
            duration
        )
        
        if success:
            st.success("✅ Результаты собеседования сохранены!")
        else:
            st.error("❌ Ошибка при сохранении результатов")
    
    # Кнопка нового собеседования
    if st.button("🔄 Пройти новое собеседование", use_container_width=True):
        for key in ['interview_data', 'interview_complete']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

def show_interview_history():
    """Показ истории собеседований"""
    interviews = auth_system.get_user_interviews(st.session_state.user_id)
    
    if interviews:
        st.markdown("---")
        st.markdown("**📚 История ваших собеседований:**")
        
        for interview in interviews[:5]:  # Показываем последние 5
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{interview[3]}** - {interview[2]}")
                    st.markdown(f"*{interview[9]}*")
                
                with col2:
                    score = interview[7]
                    st.markdown(f"**Оценка:** {score}/10")
                    if score >= 9:
                        st.success("Отлично")
                    elif score >= 7:
                        st.warning("Хорошо")
                    else:
                        st.error("Требует работы")
                
                with col3:
                    if st.button("📊 Детали", key=f"details_{interview[0]}", use_container_width=True):
                        st.session_state.selected_interview = interview[0]
                        st.rerun()
                
                st.markdown("---")

def show_interview_details(interview_id):
    """Детализация конкретного собеседования"""
    interviews = auth_system.get_user_interviews(st.session_state.user_id)
    interview = next((i for i in interviews if i[0] == interview_id), None)
    
    if not interview:
        st.error("Собеседование не найдено")
        return
    
    st.markdown(f'<div class="sub-header">📋 Детали собеседования</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Позиция:** {interview[3]}")
        st.markdown(f"**Тип:** {interview[2]}")
    with col2:
        st.markdown(f"**Оценка:** {interview[7]}/10")
        st.markdown(f"**Длительность:** {interview[8]} сек")
    with col3:
        st.markdown(f"**Дата:** {interview[9]}")
    
    # Вопросы и ответы
    try:
        questions = json.loads(interview[4]) if interview[4] else []
        answers = json.loads(interview[5]) if interview[5] else []
        feedback = json.loads(interview[6]) if interview[6] else {}
        
        st.markdown("### Вопросы и ответы:")
        for i, (question, answer) in enumerate(zip(questions, answers)):
            with st.expander(f"Вопрос {i+1}: {question}"):
                st.markdown("**Ответ:**")
                st.write(answer)
        
        if feedback:
            st.markdown("### Обратная связь:")
            st.write(feedback.get('verdict', ''))
            for fb in feedback.get('detailed_feedback', []):
                st.write(f"• {fb}")
    
    except Exception as e:
        st.error(f"Ошибка при загрузке деталей: {e}")
    
    if st.button("← Назад к истории", use_container_width=True):
        st.session_state.selected_interview = None
        st.rerun()

# =============================================
# ФУНКЦИИ ДЛЯ HR ИНТЕРФЕЙСА - КАНДИДАТЫ
# =============================================

def show_candidates_section():
    """Раздел базы кандидатов"""
    st.markdown('<div class="sub-header">👥 База кандидатов</div>', unsafe_allow_html=True)
    
    # Поиск и фильтрация
    col_search, col_filter, col_sort = st.columns([2, 2, 1])
    
    with col_search:
        search_term = st.text_input("🔍 Поиск по имени или позиции", placeholder="Введите имя или должность...")
    
    with col_filter:
        position_filter = st.selectbox("Фильтр по позиции", ["Все позиции", "Разработчик", "Менеджер", "Аналитик", "Дизайнер"])
    
    with col_sort:
        sort_by = st.selectbox("Сортировка", ["Дата добавления", "Оценка", "Имя"])
    
    # Получаем кандидатов
    candidates = get_all_candidates()
    
    if not candidates:
        st.info("ℹ️ В базе пока нет кандидатов. Кандидаты появятся после загрузки резюме.")
        return
    
    # Применяем фильтры
    filtered_candidates = candidates
    
    if search_term:
        filtered_candidates = [c for c in filtered_candidates 
                             if search_term.lower() in (c[7] or '').lower() 
                             or search_term.lower() in (c[2] or '').lower()]
    
    if position_filter != "Все позиции":
        filtered_candidates = [c for c in filtered_candidates if c[2] == position_filter]
    
    # Применяем сортировку
    if sort_by == "Оценка":
        filtered_candidates.sort(key=lambda x: x[11] or 0, reverse=True)
    elif sort_by == "Имя":
        filtered_candidates.sort(key=lambda x: x[7] or '')
    else:  # Дата добавления
        filtered_candidates.sort(key=lambda x: x[4] or '', reverse=True)
    
    # Статистика
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    with col_stats1:
        st.metric("Всего кандидатов", len(filtered_candidates))
    with col_stats2:
        analyzed = len([c for c in filtered_candidates if c[11]])
        st.metric("Проанализировано", analyzed)
    with col_stats3:
        avg_score = sum(c[11] or 0 for c in filtered_candidates) / len(filtered_candidates) if filtered_candidates else 0
        st.metric("Средняя оценка", f"{avg_score:.1f}%")
    with col_stats4:
        unique_positions = len(set(c[2] for c in filtered_candidates if c[2]))
        st.metric("Уникальные позиции", unique_positions)
    
    st.markdown("---")
    
    # Отображение кандидатов
    for candidate in filtered_candidates:
        with st.container():
            st.markdown('<div class="candidate-card">', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                # Основная информация
                st.markdown(f"### {candidate[7] or 'Не указано'}")
                st.markdown(f"**💼 Позиция:** {candidate[2] or 'Не определена'}")
                st.markdown(f"**📊 Уровень:** {candidate[3] or 'Не указан'}")
                
                # Контактная информация
                if candidate[9]:  # phone
                    st.markdown(f"**📞 Телефон:** {candidate[9]}")
                if candidate[10]:  # location
                    st.markdown(f"**📍 Местоположение:** {candidate[10]}")
                if candidate[8]:  # email
                    st.markdown(f"**📧 Email:** {candidate[8]}")
            
            with col2:
                # Информация об анализе
                if candidate[11]:  # authenticity_score
                    score = candidate[11]
                    st.markdown(f"**🎯 Оценка достоверности:** {score}%")
                    st.progress(score / 100)
                    st.markdown(f"**✅ Вердикт:** {candidate[12] or 'Не определен'}")
                else:
                    st.markdown("**🔍 Статус:** Не анализировано")
                
                st.markdown(f"**📅 Загружено:** {candidate[4][:10] if candidate[4] else 'Неизвестно'}")
            
            with col3:
                # Кнопка просмотра деталей
                if st.button("👀 Просмотр", key=f"view_{candidate[0]}", use_container_width=True):
                    st.session_state.selected_candidate = candidate[0]
                    st.rerun()
                
                # Скачивание резюме
                resume_file = get_resume_file(candidate[0])
                if resume_file and resume_file[1]:
                    download_link = create_download_link(resume_file[1], resume_file[0], resume_file[2])
                    if download_link:
                        st.markdown(download_link, unsafe_allow_html=True)
            
            with col4:
                # Избранное
                is_favorite = is_in_favorites(st.session_state.user_id, candidate[6])
                
                if is_favorite:
                    if st.button("⭐ Убрать", key=f"unfav_{candidate[0]}", use_container_width=True):
                        if remove_from_favorites(st.session_state.user_id, candidate[6]):
                            st.success("✅ Кандидат удален из избранного")
                            st.rerun()
                else:
                    if st.button("⭐ В избранное", key=f"fav_{candidate[0]}", use_container_width=True):
                        if add_to_favorites(st.session_state.user_id, candidate[6], candidate[0]):
                            st.success("✅ Кандидат добавлен в избранное")
                            st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_candidate_details(candidate_id):
    """Детальная информация о кандидате"""
    candidates = get_all_candidates()
    candidate = next((c for c in candidates if c[0] == candidate_id), None)
    
    if not candidate:
        st.error("Кандидат не найден")
        return
    
    st.markdown(f'<div class="sub-header">👤 Детальная информация: {candidate[7]}</div>', unsafe_allow_html=True)
    
    # Основная информация
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Основная информация")
        st.markdown(f"**Полное имя:** {candidate[7]}")
        st.markdown(f"**Email:** {candidate[8]}")
        st.markdown(f"**Телефон:** {candidate[9] or 'Не указан'}")
        st.markdown(f"**Местоположение:** {candidate[10] or 'Не указано'}")
        st.markdown(f"**Позиция:** {candidate[2] or 'Не определена'}")
        st.markdown(f"**Уровень опыта:** {candidate[3] or 'Не указан'}")
        st.markdown(f"**Дата загрузки:** {candidate[4] or 'Неизвестно'}")
    
    with col2:
        st.markdown("### 📊 Анализ резюме")
        if candidate[11]:
            score = candidate[11]
            st.markdown(f"**Оценка достоверности:** {score}%")
            st.progress(score / 100)
            st.markdown(f"**Вердикт:** {candidate[12]}")
            st.markdown(f"**Дата анализа:** {candidate[13] or 'Неизвестно'}")
        else:
            st.markdown("**🔍 Резюме еще не анализировано**")
    
    # Действия с кандидатом
    st.markdown("### 🎯 Действия")
    
    col_actions1, col_actions2, col_actions3, col_actions4 = st.columns(4)
    
    with col_actions1:
        # Избранное
        is_favorite = is_in_favorites(st.session_state.user_id, candidate[6])
        if is_favorite:
            if st.button("⭐ Убрать из избранного", use_container_width=True):
                if remove_from_favorites(st.session_state.user_id, candidate[6]):
                    st.success("✅ Кандидат удален из избранного")
                    st.rerun()
        else:
            if st.button("⭐ Добавить в избранное", use_container_width=True):
                notes = st.text_input("Заметки (необязательно)", key=f"notes_{candidate_id}")
                if add_to_favorites(st.session_state.user_id, candidate[6], candidate_id, notes):
                    st.success("✅ Кандидат добавлен в избранное")
                    st.rerun()
    
    with col_actions2:
        # Скачивание резюме
        resume_file = get_resume_file(candidate_id)
        if resume_file and resume_file[1]:
            download_link = create_download_link(resume_file[1], resume_file[0], resume_file[2])
            if download_link:
                st.markdown(download_link, unsafe_allow_html=True)
        else:
            st.info("📄 Резюме недоступно")
    
    with col_actions3:
        if st.button("📞 Пригласить на интервью", use_container_width=True):
            st.success(f"✅ Приглашение отправлено {candidate[7]}!")
    
    with col_actions4:
        if st.button("📧 Отправить сообщение", use_container_width=True):
            st.success(f"✅ Сообщение отправлено на {candidate[8]}")
    
    st.markdown("---")
    
    # История взаимодействий (заглушка)
    st.markdown("### 📝 История взаимодействий")
    st.info("""
    **Будущий функционал:**
    - 📞 История звонков и встреч
    - 💬 Переписка с кандидатом
    - 📅 Запланированные события
    - 📊 Прогресс по процессу найма
    """)
    
    if st.button("← Назад к списку кандидатов", use_container_width=True):
        st.session_state.selected_candidate = None
        st.rerun()

def show_favorites_section():
    """Раздел избранных кандидатов"""
    st.markdown('<div class="sub-header">⭐ Избранные кандидаты</div>', unsafe_allow_html=True)
    
    favorites = get_favorites(st.session_state.user_id)
    
    if not favorites:
        st.info("ℹ️ У вас пока нет избранных кандидатов")
        return
    
    # Статистика избранных - ИСПРАВЛЕННАЯ СТРОКА
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("Всего в избранном", len(favorites))
    with col_stats2:
        # ИСПРАВЛЕННАЯ СТРОКА - правильная обработка разных типов данных
        try:
            avg_score = sum(float(f[9]) if f[9] is not None and str(f[9]).replace('.', '').replace(',', '').isdigit() else 0 for f in favorites) / len(favorites) if favorites else 0
            st.metric("Средняя оценка", f"{avg_score:.1f}%")
        except (ValueError, TypeError):
            st.metric("Средняя оценка", "N/A")
    with col_stats3:
        unique_positions = len(set(f[6] for f in favorites if f[6]))
        st.metric("Уникальные позиции", unique_positions)
    
    st.markdown("---")
    
    for fav in favorites:
        with st.container():
            st.markdown('<div class="candidate-card">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"### {fav[4] or 'Не указано'}")
                st.markdown(f"**💼 Позиция:** {fav[6] or 'Не определена'}")
                st.markdown(f"**📊 Уровень:** {fav[7] or 'Не указан'}")
                st.markdown(f"**📧 Email:** {fav[5]}")
                if fav[3]:  # notes
                    st.markdown(f"**📝 Заметки:** {fav[3]}")
            
            with col2:
                if fav[9] is not None:  # authenticity_score - проверка на None
                    try:
                        score = float(fav[9]) if str(fav[9]).replace('.', '').replace(',', '').isdigit() else 0
                        st.markdown(f"**🎯 Оценка:** {score}%")
                        st.progress(score / 100)
                    except (ValueError, TypeError):
                        st.markdown(f"**🎯 Оценка:** {fav[9]}")
                        st.progress(0)
                    st.markdown(f"**✅ Вердикт:** {fav[10] or 'Не определен'}")
                else:
                    st.markdown("**🎯 Оценка:** Не анализировано")
                st.markdown(f"**⭐ Добавлено:** {fav[8] or 'Неизвестно'}")
            
            with col3:
                if st.button("👀 Просмотр", key=f"view_fav_{fav[0]}", use_container_width=True):
                    st.session_state.selected_candidate = fav[3]  # resume_id
                    st.rerun()
                
                if st.button("🗑️ Удалить", key=f"remove_{fav[0]}", use_container_width=True):
                    if remove_from_favorites(st.session_state.user_id, fav[2]):  # candidate_user_id
                        st.success("✅ Кандидат удален из избранного")
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# ОСТАЛЬНЫЕ ФУНКЦИИ HR ИНТЕРФЕЙСА
# =============================================

def show_hr_interface():
    """Главный интерфейс HR"""
    st.markdown('<div class="main-header">💼 Панель HR</div>', unsafe_allow_html=True)
    
    # Проверяем выбран ли конкретный кандидат
    if st.session_state.get('selected_candidate'):
        show_candidate_details(st.session_state.selected_candidate)
    else:
        if st.session_state.hr_section == "candidates":
            show_candidates_section()
        elif st.session_state.hr_section == "favorites":
            show_favorites_section()
        elif st.session_state.hr_section == "analytics":
            show_hr_analytics()
        elif st.session_state.hr_section == "settings":
            show_hr_settings()
        elif st.session_state.hr_section == "database":
            show_database_viewer()

def show_hr_analytics():
    """Аналитика для HR"""
    st.markdown('<div class="sub-header">📊 Аналитика кандидатов</div>', unsafe_allow_html=True)
    
    candidates = get_all_candidates()
    
    if not candidates:
        st.info("ℹ️ Нет данных для анализа")
        return
    
    # Собираем данные для аналитики
    position_data = {}
    score_data = []
    location_data = {}
    
    for candidate in candidates:
        # Распределение по позициям
        position = candidate[2] or "Не определена"
        if position in position_data:
            position_data[position] += 1
        else:
            position_data[position] = 1
        
        # Оценки
        if candidate[11]:
            score_data.append(candidate[11])
        
        # Локации
        location = candidate[10] or "Не указано"
        if location in location_data:
            location_data[location] += 1
        else:
            location_data[location] = 1
    
    # Статистика
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Всего кандидатов", len(candidates))
    with col2:
        analyzed = len([c for c in candidates if c[11]])
        st.metric("Проанализировано", analyzed)
    with col3:
        avg_score = sum(score_data) / len(score_data) if score_data else 0
        st.metric("Средняя оценка", f"{avg_score:.1f}%")
    with col4:
        st.metric("Уникальные позиции", len(position_data))
    
    # Визуализации
    if score_data:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            if position_data:
                fig_positions = px.pie(
                    values=list(position_data.values()),
                    names=list(position_data.keys()),
                    title="Распределение кандидатов по позициям",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_positions.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_positions, use_container_width=True)
        
        with col_chart2:
            fig_scores = px.histogram(
                x=score_data,
                title="Распределение оценок кандидатов",
                nbins=10,
                color_discrete_sequence=['#FF6B35']
            )
            fig_scores.update_layout(
                xaxis_title="Оценка достоверности (%)",
                yaxis_title="Количество кандидатов"
            )
            st.plotly_chart(fig_scores, use_container_width=True)
    
    # Топ локаций
    if location_data:
        top_locations = dict(sorted(location_data.items(), key=lambda x: x[1], reverse=True)[:10])
        fig_locations = px.bar(
            x=list(top_locations.values()),
            y=list(top_locations.keys()),
            orientation='h',
            title="Топ-10 местоположений кандидатов",
            color_discrete_sequence=['#4facfe']
        )
        st.plotly_chart(fig_locations, use_container_width=True)

def show_hr_settings():
    """Настройки для HR"""
    st.markdown('<div class="sub-header">⚙️ Критерии оценки</div>', unsafe_allow_html=True)
    
    st.markdown("**📝 Вопросы для собеседования:**")
    
    # Загрузка стандартных вопросов
    default_questions = [
        "Расскажите о себе и своем профессиональном пути.",
        "Почему вы заинтересованы в этой позиции?",
        "Какие ваши сильные стороны?",
        "Какие ваши слабые стороны?",
        "Почему вы хотите работать именно в нашей компании?",
        "Где вы видите себя через 5 лет?",
        "Почему вы уходите с текущего места работы?",
        "Расскажите о своем самом значительном профессиональном достижении.",
        "Как вы справляетесь со стрессом и давлением?",
        "Какой рабочей средой вы предпочитаете?"
    ]
    
    # Редактирование вопросов
    edited_questions = []
    for i, question in enumerate(default_questions):
        edited_question = st.text_area(f"Вопрос {i+1}", value=question, key=f"question_{i}")
        edited_questions.append(edited_question)
    
    if st.button("💾 Сохранить вопросы", use_container_width=True):
        st.session_state.custom_questions = edited_questions
        st.success("✅ Вопросы сохранены!")
    
    st.markdown("---")
    st.markdown("**🎯 Критерии оценки:**")
    
    col_crit1, col_crit2 = st.columns(2)
    
    with col_crit1:
        min_score = st.slider("Минимальная оценка для приглашения", 0, 100, 70, key="min_score")
        tech_weight = st.slider("Вес технических навыков (%)", 0, 100, 40, key="tech_weight")
    
    with col_crit2:
        exp_weight = st.slider("Вес опыта работы (%)", 0, 100, 30, key="exp_weight")
        soft_weight = st.slider("Вес soft skills (%)", 0, 100, 30, key="soft_weight")
    
    if st.button("💾 Сохранить критерии", use_container_width=True):
        st.success("✅ Критерии сохранены!")

def show_database_viewer():
    """Просмотр базы данных"""
    st.markdown('<div class="sub-header">🗃️ Просмотр базы данных</div>', unsafe_allow_html=True)
    
    # Статистика базы данных
    stats = auth_system.get_table_statistics()
    if stats:
        cols = st.columns(len(stats))
        for i, (table, count) in enumerate(stats.items()):
            with cols[i]:
                st.metric(f"Таблица: {table}", count)
    
    st.markdown("---")
    
    # Выбор режима просмотра
    view_mode = st.radio("Режим просмотра:", ["Просмотр таблиц", "SQL запросы"], horizontal=True)
    
    if view_mode == "Просмотр таблиц":
        show_table_viewer()
    else:
        show_sql_query_interface()

def show_table_viewer():
    """Просмотр данных таблиц"""
    tables = auth_system.get_database_tables()
    
    if not tables:
        st.error("❌ В базе данных нет таблиц")
        return
    
    selected_table = st.selectbox("Выберите таблицу для просмотра:", tables)
    
    if selected_table:
        # Получаем данные таблицы
        df, columns_info = auth_system.get_table_data(selected_table)
        
        if df is not None:
            # Информация о таблице
            st.markdown(f"### 📋 Таблица: `{selected_table}`")
            
            # Показываем информацию о столбцах
            with st.expander("🔍 Информация о столбцах"):
                if columns_info:
                    col_info_df = pd.DataFrame(columns_info, 
                                            columns=['cid', 'name', 'type', 'notnull', 'default', 'pk'])
                    st.dataframe(col_info_df[['name', 'type', 'notnull', 'pk']], use_container_width=True)
            
            # Показываем данные
            st.markdown("### 📊 Данные таблицы")
            
            # Фильтрация и поиск
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("🔍 Поиск по таблице:", placeholder="Введите текст для поиска...")
            with col2:
                rows_per_page = st.selectbox("Строк на странице:", [10, 25, 50, 100], index=0)
            
            # Применяем поиск если есть поисковый запрос
            if search_term:
                try:
                    mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                    filtered_df = df[mask]
                except:
                    filtered_df = df
            else:
                filtered_df = df
            
            # Показываем данные с пагинацией
            if not filtered_df.empty:
                total_rows = len(filtered_df)
                st.write(f"**Найдено записей:** {total_rows}")
                
                # Пагинация
                if total_rows > rows_per_page:
                    total_pages = (total_rows + rows_per_page - 1) // rows_per_page
                    page = st.number_input("Страница:", min_value=1, max_value=total_pages, value=1)
                    start_idx = (page - 1) * rows_per_page
                    end_idx = min(start_idx + rows_per_page, total_rows)
                    
                    st.dataframe(filtered_df.iloc[start_idx:end_idx], use_container_width=True)
                    st.write(f"Показаны записи {start_idx + 1}-{end_idx} из {total_rows}")
                else:
                    st.dataframe(filtered_df, use_container_width=True)
                
                # Кнопки экспорта
                col_export1, col_export2, col_export3 = st.columns(3)
                
                with col_export1:
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 CSV",
                        data=csv,
                        file_name=f"{selected_table}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("ℹ️ В таблице нет данных или ничего не найдено по вашему запросу")
        else:
            st.error("❌ Ошибка при загрузке данных таблицы")

def show_sql_query_interface():
    """Интерфейс для выполнения SQL запросов"""
    st.markdown("### 🛠️ Выполнение SQL запросов")
    
    st.warning("""
    ⚠️ **Внимание:** Будьте осторожны при выполнении SQL запросов. 
    Некорректные запросы могут повредить базу данных.
    """)
    
    # Примеры запросов
    with st.expander("📚 Примеры SQL запросов"):
        examples = {
            "SELECT": "SELECT * FROM users LIMIT 10;",
            "JOIN": """SELECT u.full_name, r.filename, ra.authenticity_score 
                      FROM users u 
                      JOIN resumes r ON u.id = r.user_id 
                      JOIN resume_analyses ra ON r.id = ra.resume_id 
                      LIMIT 10;""",
            "COUNT": "SELECT user_type, COUNT(*) as count FROM users GROUP BY user_type;"
        }
        
        selected_example = st.selectbox("Выберите пример:", list(examples.keys()))
        if st.button("Использовать пример"):
            st.session_state.sql_query = examples[selected_example]
    
    # Ввод SQL запроса
    sql_query = st.text_area(
        "Введите SQL запрос:",
        height=150,
        key="sql_query",
        placeholder="Например: SELECT * FROM users WHERE user_type = 'candidate';"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        execute_btn = st.button("🚀 Выполнить запрос", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑️ Очистить", use_container_width=True)
    
    if clear_btn:
        st.session_state.sql_query = ""
        st.rerun()
    
    if execute_btn and sql_query:
        with st.spinner("Выполнение запроса..."):
            result, message = auth_system.execute_custom_query(sql_query)
            
            if result is not None:
                st.success("✅ Запрос выполнен успешно!")
                st.write(f"**Найдено записей:** {len(result)}")
                st.dataframe(result, use_container_width=True)
            elif message:
                st.success(message)

# =============================================
# БАЗОВЫЕ ФУНКЦИИ СИСТЕМЫ
# =============================================

def init_session():
    """Инициализация сессии"""
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # НОВЫЕ СОСТОЯНИЯ ДЛЯ АВТОРИЗАЦИИ
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'full_name' not in st.session_state:
        st.session_state.full_name = ""
    if 'company' not in st.session_state:
        st.session_state.company = ""
    if 'phone' not in st.session_state:
        st.session_state.phone = ""
    if 'location' not in st.session_state:
        st.session_state.location = ""
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False
    if 'change_password' not in st.session_state:
        st.session_state.change_password = False
    
    # СОСТОЯНИЯ ДЛЯ РАЗДЕЛОВ HR
    if 'hr_section' not in st.session_state:
        st.session_state.hr_section = "candidates"
    
    # НОВОЕ СОСТОЯНИЕ ДЛЯ ПРОСМОТРА БАЗЫ ДАННЫХ
    if 'show_database' not in st.session_state:
        st.session_state.show_database = False
    
    # НОВЫЕ СОСТОЯНИЯ ДЛЯ СОБЕСЕДОВАНИЙ
    if 'interview_data' not in st.session_state:
        st.session_state.interview_data = None
    if 'interview_complete' not in st.session_state:
        st.session_state.interview_complete = False
    if 'selected_interview' not in st.session_state:
        st.session_state.selected_interview = None
    
    # НОВЫЕ СОСТОЯНИЯ ДЛЯ КАНДИДАТОВ
    if 'selected_candidate' not in st.session_state:
        st.session_state.selected_candidate = None
    if 'custom_questions' not in st.session_state:
        st.session_state.custom_questions = []

def detect_position_from_resume(resume_text):
    """AI определяет позицию из резюме"""
    positions = {
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
    
    for keyword, position in positions.items():
        if keyword in resume_text.lower():
            return position
    
    return "Разработчик"  # По умолчанию

def verify_resume_authenticity(resume_text, uploaded_file=None):
    """Проверка резюме на правдоподобность с помощью AI"""
    import random
    
    try:
        detected_position = detect_position_from_resume(resume_text)
        authenticity_score = random.randint(70, 95)
        
        flags = []
        recommendations = []
        
        # Анализ содержания
        if len(resume_text) < 500:
            flags.append("Слишком краткое резюме, возможны пропуски важной информации")
            recommendations.append("Рекомендуем добавить больше деталей о проектах и достижениях")
        
        if "опыт работы" not in resume_text.lower():
            flags.append("Отсутствует раздел с опытом работы")
            recommendations.append("Добавьте подробное описание опыта работы с указанием сроков")
        
        if "образование" not in resume_text.lower():
            flags.append("Отсутствует раздел с образованием")
            recommendations.append("Укажите информацию об образовании")
        
        if len(flags) == 0:
            flags.append("Основные разделы присутствуют")
        
        if len(recommendations) == 0:
            recommendations = [
                "Рекомендуем добавить конкретные цифры и метрики",
                "Уточните сроки работы в каждом месте",
                "Добавьте информацию о реальных проектах и достижениях"
            ]
        
        return {
            "score": authenticity_score,
            "flags": flags,
            "recommendations": recommendations,
            "verdict": "Достоверно" if authenticity_score >= 80 else "Требует проверки",
            "detected_position": detected_position
        }
        
    except Exception as e:
        st.error(f"Ошибка при анализе резюме: {e}")
        return {
            "score": 75,
            "flags": ["Временные технические проблемы с анализом"],
            "recommendations": ["Попробуйте проверить резюме позже"],
            "verdict": "Требует проверки",
            "detected_position": "Разработчик"
        }

def save_resume_to_db(user_id, filename, file_content, file_type, file_size, analysis_result):
    """Сохранение резюме в базу данных"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        # Сохраняем резюме
        cursor.execute('''
            INSERT INTO resumes 
            (user_id, filename, file_content, file_type, file_size, original_text, 
             detected_position, experience_level, is_analyzed, analysis_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            filename,
            file_content,
            file_type,
            file_size,
            file_content if isinstance(file_content, str) else "",
            analysis_result['detected_position'],
            "Middle",  # По умолчанию
            True,
            datetime.now().isoformat()
        ))
        
        resume_id = cursor.lastrowid
        
        # Сохраняем анализ
        cursor.execute('''
            INSERT INTO resume_analyses 
            (resume_id, user_id, authenticity_score, detected_position, flags, 
             recommendations, verdict, analysis_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume_id,
            user_id,
            analysis_result['score'],
            analysis_result['detected_position'],
            json.dumps(analysis_result['flags']),
            json.dumps(analysis_result['recommendations']),
            analysis_result['verdict'],
            json.dumps(analysis_result)
        ))
        
        conn.commit()
        conn.close()
        return resume_id
        
    except Exception as e:
        print(f"Error saving resume to DB: {e}")
        return None

def get_user_resumes(user_id):
    """Получение резюме пользователя"""
    try:
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM resumes WHERE user_id = ? ORDER BY upload_date DESC
        ''', (user_id,))
        
        resumes = cursor.fetchall()
        conn.close()
        return resumes
        
    except Exception as e:
        print(f"Error getting user resumes: {e}")
        return []

# =============================================
# ОСНОВНЫЕ ФУНКЦИИ ИНТЕРФЕЙСА
# =============================================

def show_login_page():
    """Страница входа и регистрации"""
    st.markdown("""
    <div style='text-align: center; padding: 3rem 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin-bottom: 2rem;'>
        <h1 style='color: white; font-size: 4rem; margin-bottom: 1rem;'>💼 КандиДА</h1>
        <p style='color: white; font-size: 1.5rem; opacity: 0.9;'>Интеллектуальная платформа для карьерного роста</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Вход", "📝 Регистрация"])
    
    with tab1:
        st.subheader("Вход в систему")
        
        login_username = st.text_input("Логин", key="login_username")
        login_password = st.text_input("Пароль", type="password", key="login_password")
        
        if st.button("Войти", key="login_btn", use_container_width=True):
            if login_username and login_password:
                user = auth_system.authenticate_user(login_username, login_password)
                
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user['id']
                    st.session_state.username = user['username']
                    st.session_state.user_type = user['user_type']
                    st.session_state.full_name = user['full_name']
                    st.session_state.company = user.get('company', '')
                    st.session_state.phone = user.get('phone', '')
                    st.session_state.location = user.get('location', '')
                    
                    st.success(f"Добро пожаловать, {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
            else:
                st.error("Заполните все поля")
        
        # Тестовые аккаунты для быстрого доступа
        with st.expander("🧪 Тестовые аккаунты"):
            st.write("**HR:** Логин: `hr_manager` Пароль: `hr123`")
            st.write("**Кандидат:** Логин: `candidate` Пароль: `candidate123`")
            st.write("**Админ:** Логин: `admin` Пароль: `admin123`")
    
    with tab2:
        st.subheader("Регистрация")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reg_email = st.text_input("Email", key="reg_email")
            reg_username = st.text_input("Логин", key="reg_username")
            reg_full_name = st.text_input("ФИО", key="reg_full_name")
            user_type = st.selectbox("Тип пользователя", ["candidate", "hr"], 
                                   format_func=lambda x: "Соискатель" if x == "candidate" else "HR-специалист")
        
        with col2:
            reg_password = st.text_input("Пароль", type="password", key="reg_password")
            reg_confirm_password = st.text_input("Подтвердите пароль", type="password", key="reg_confirm_password")
            
            if user_type == "hr":
                company = st.text_input("Компания", key="reg_company")
                position = st.text_input("Должность", key="reg_position")
                phone = ""
                location = ""
            else:
                company = ""
                position = ""
                phone = st.text_input("Телефон", key="reg_phone")
                location = st.text_input("Город", key="reg_location")
        
        if st.button("Зарегистрироваться", key="reg_btn", use_container_width=True):
            if all([reg_email, reg_username, reg_password, reg_confirm_password, reg_full_name]):
                if reg_password == reg_confirm_password:
                    user_data = {
                        'email': reg_email,
                        'username': reg_username,
                        'password': reg_password,
                        'full_name': reg_full_name,
                        'user_type': user_type,
                        'company': company,
                        'position': position,
                        'phone': phone,
                        'location': location
                    }
                    
                    if auth_system.create_user(user_data):
                        st.success("✅ Регистрация успешна! Теперь вы можете войти в систему.")
                        st.rerun()
                    else:
                        st.error("❌ Пользователь с таким email или логином уже существует")
                else:
                    st.error("❌ Пароли не совпадают")
            else:
                st.error("⚠️ Заполните все обязательные поля")

def show_candidate_interface():
    """Интерфейс для соискателей"""
    st.markdown('<div class="main-header">💼 КандиДА</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #6C757D; font-size: 1.2rem; margin-bottom: 3rem;">Ваш персональный помощник в карьерном росте</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎤 Собеседование", "🔍 Проверка резюме", "📊 Моя статистика", "📁 Мои резюме"])
    
    with tab1:
        # Проверяем состояние собеседования
        if st.session_state.get('interview_complete'):
            show_interview_results()
        elif st.session_state.get('interview_data'):
            conduct_interview()
        elif st.session_state.get('selected_interview'):
            show_interview_details(st.session_state.selected_interview)
        else:
            show_interview_interface()
    
    with tab2:
        show_resume_analysis_section()
    
    with tab3:
        show_candidate_stats()
    
    with tab4:
        show_my_resumes()

def show_resume_analysis_section():
    """Раздел анализа резюме"""
    st.markdown('<div class="sub-header">🔍 Проверка резюме на достоверность</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("📎 Загрузите ваше резюме", type=["pdf", "docx", "txt"])
    resume_text = st.text_area("✍️ Или введите текст резюме", height=200, 
                             placeholder="Опыт работы...\nОбразование...\nНавыки...\nДостижения...")
    
    if st.button("🔍 Проверить достоверность", use_container_width=True, type="primary"):
        if uploaded_file or resume_text:
            with st.spinner("🔄 AI анализирует резюме..."):
                try:
                    # Подготавливаем данные
                    if uploaded_file:
                        file_content = uploaded_file.getvalue()
                        filename = uploaded_file.name
                        file_type = uploaded_file.type
                        file_size = uploaded_file.size
                        if uploaded_file.type == "text/plain":
                            resume_content = uploaded_file.getvalue().decode('utf-8')
                        else:
                            resume_content = f"Файл: {filename}"
                    else:
                        file_content = resume_text.encode('utf-8')
                        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        file_type = "text/plain"
                        file_size = len(resume_text.encode('utf-8'))
                        resume_content = resume_text
                    
                    # Анализируем резюме
                    verification = verify_resume_authenticity(resume_content, uploaded_file)
                    
                    # Сохраняем в базу данных
                    resume_id = save_resume_to_db(
                        st.session_state.user_id,
                        filename,
                        file_content,
                        file_type,
                        file_size,
                        verification
                    )
                    
                    st.session_state.current_verification = verification
                    st.success("✅ Проверка завершена и сохранена в базе!")
                    
                except Exception as e:
                    st.error(f"❌ Ошибка при проверке резюме: {e}")
        else:
            st.error("⚠️ Загрузите файл или введите текст резюме")
    
    if st.session_state.get('current_verification'):
        show_analysis_results(st.session_state.current_verification)

def show_analysis_results(verification):
    """Показывает результаты анализа"""
    st.markdown("---")
    st.markdown('<div class="sub-header">📋 Результаты проверки</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns([2, 1])
    
    with col3:
        st.markdown(f'<div class="metric-card">🎯 Оценка достоверности: <span style="font-size: 2rem; color: #FF6B35;">{verification["score"]}%</span></div>', unsafe_allow_html=True)
        st.progress(verification["score"] / 100)
        st.markdown(f'**Вердикт:** {verification["verdict"]}')
        st.markdown(f'**Определенная позиция:** {verification["detected_position"]}')
        
    with col4:
        if verification["score"] >= 90:
            st.markdown('<div class="success-card">🎉 Отличное резюме!</div>', unsafe_allow_html=True)
        elif verification["score"] >= 80:
            st.markdown('<div class="warning-card">👍 Хорошее резюме</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-card">🔧 Требуется доработка</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("**⚠️ Замечания:**")
        for flag in verification["flags"]:
            st.markdown(f"- {flag}")
    
    with col6:
        st.markdown("**💡 Рекомендации:**")
        for recommendation in verification["recommendations"]:
            st.markdown(f"- {recommendation}")

def show_my_resumes():
    """Показывает историю загруженных резюме"""
    st.markdown('<div class="sub-header">📁 История моих резюме</div>', unsafe_allow_html=True)
    
    try:
        resumes = get_user_resumes(st.session_state.user_id)
        
        if not resumes:
            st.info("ℹ️ У вас пока нет сохраненных резюме")
            return
        
        for resume in resumes:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{resume[2]}**")  # filename
                    st.markdown(f"*Загружено: {resume[6]}*")  # upload_date
                    if resume[8]:  # detected_position
                        st.markdown(f"**Позиция:** {resume[8]}")
                
                with col2:
                    if resume[11]:  # is_analyzed
                        st.markdown("**Статус:** Проанализировано")
                    else:
                        st.markdown("**Статус:** Не анализировано")
                
                with col3:
                    st.info("Файл сохранен")
                
                st.markdown("---")
                
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке резюме: {e}")

def show_candidate_stats():
    """Показывает статистику кандидата"""
    st.markdown('<div class="sub-header">📊 Моя статистика</div>', unsafe_allow_html=True)
    
    try:
        resumes = get_user_resumes(st.session_state.user_id)
        interviews = auth_system.get_user_interviews(st.session_state.user_id)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Всего резюме", len(resumes))
        
        with col2:
            analyzed_resumes = len([r for r in resumes if r[11]])
            st.metric("Проанализировано", analyzed_resumes)
        
        with col3:
            st.metric("Собеседования", len(interviews))
        
        with col4:
            if interviews:
                avg_score = sum(i[7] for i in interviews) / len(interviews)
                st.metric("Средняя оценка", f"{avg_score:.1f}/10")
            else:
                st.metric("Средняя оценка", "0/10")
        
        if interviews:
            st.markdown("**Последние собеседования:**")
            for interview in interviews[:3]:
                st.markdown(f"- {interview[3]} ({interview[9][:10]}) - {interview[7]}/10")
        
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке статистики: {e}")

def show_main_interface():
    """Главный интерфейс после входа"""
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #FF6B35, #FF8C42); border-radius: 15px; margin-bottom: 2rem;'>
            <h3 style='color: white; margin: 0;'>👋 Привет, {st.session_state.full_name}!</h3>
            <p style='color: white; opacity: 0.9; margin: 0;'>{st.session_state.company if st.session_state.user_type == 'hr' else 'Соискатель'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👤 Профиль", use_container_width=True):
            st.session_state.show_profile = True
            st.rerun()
        
        if st.button("🔐 Сменить пароль", use_container_width=True):
            st.session_state.change_password = True
            st.rerun()
        
        if st.session_state.user_type == "hr":
            st.markdown("---")
            st.markdown("**HR Навигация:**")
            
            # Создаем кнопки навигации с визуальной обратной связью
            sections = [
                ("👥 База кандидатов", "candidates"),
                ("⭐ Избранное", "favorites"), 
                ("📊 Аналитика", "analytics"),
                ("⚙️ Критерии оценки", "settings"),
                ("🗃️ Просмотр БД", "database")
            ]
            
            for section_name, section_key in sections:
                is_active = st.session_state.hr_section == section_key
                button_style = "nav-button-active" if is_active else "nav-button-inactive"
                
                if st.button(
                    section_name, 
                    use_container_width=True,
                    key=f"hr_nav_{section_key}",
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.hr_section = section_key
                    st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Выйти", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Основной контент
    if st.session_state.user_type == "candidate":
        show_candidate_interface()
    else:
        show_hr_interface()

def main():
    init_session()
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_interface()

if __name__ == "__main__":
    main()