import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime
import json

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
        
        # Таблица профилей кандидатов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidate_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                resume_text TEXT,
                desired_position TEXT,
                experience_level TEXT,
                skills TEXT,
                education TEXT,
                work_experience TEXT,
                salary_expectations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица анализов резюме
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                authenticity_score REAL,
                detected_position TEXT,
                flags TEXT,
                recommendations TEXT,
                verdict TEXT,
                analysis_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем тестовых пользователей если их нет
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self._create_test_users(cursor)
        
        conn.commit()
        conn.close()
    
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
                'position': 'HR Manager'
            },
            {
                'email': 'candidate@example.com',
                'username': 'candidate',
                'password': 'candidate123', 
                'full_name': 'Иван Иванов',
                'user_type': 'candidate',
                'phone': '+79991234567',
                'location': 'Москва'
            }
        ]
        
        for user_data in test_users:
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
                user_data.get('company'),
                user_data.get('position'),
                user_data.get('phone'),
                user_data.get('location')
            ))
    
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
                user_data.get('company'),
                user_data.get('position'),
                user_data.get('phone'),
                user_data.get('location')
            ))
            
            conn.commit()
            conn.close()
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
                update_data.get('company'),
                update_data.get('position'),
                update_data.get('phone'),
                update_data.get('location'),
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

# Глобальный экземпляр системы аутентификации
auth_system = AuthSystem()