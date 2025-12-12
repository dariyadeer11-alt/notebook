"""
database.py
Модуль для работы с базой данных PostgreSQL.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from contextlib import contextmanager

# Загружаем переменные окружения
load_dotenv()


class Database:
    """
    Класс для управления подключением к PostgreSQL.
    """

    # database.py
    @staticmethod
    def get_connection():
        """Создает и возвращает подключение к БД."""
        try:
            # Явно указываем параметры
            conn_params = {
                'dbname': os.getenv('DB_NAME', 'notebookk_db'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', ''),
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'connect_timeout': 10,
                # Добавляем для Windows + PostgreSQL 18
                'sslmode': 'disable',
                'client_encoding': 'UTF8'
            }

            print(
                f"🔧 Параметры подключения: host={conn_params['host']}, port={conn_params['port']}, user={conn_params['user']}")

            conn = psycopg2.connect(**conn_params)
            print("✅ Подключение установлено!")
            return conn
        except psycopg2.OperationalError as e:
            print(f"❌ Ошибка подключения: {e}")
            print("Проверьте:")
            print("1. Запущен ли PostgreSQL (services.msc)")
            print("2. Правильный ли пароль в .env")
            print("3. Может ли localhost подключиться (127.0.0.1 вместо localhost)")
            raise
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            raise

    @staticmethod
    @contextmanager
    def get_cursor():
        """
        Контекстный менеджер для работы с курсором.
        Автоматически закрывает соединение и курсор.
        """
        conn = None
        cursor = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            yield cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Ошибка БД: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def init_database():
        """
        Инициализирует базу данных: создает таблицу, если она не существует.
        """
        try:
            with Database.get_cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        body TEXT NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'todo',
                        priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Создаем индекс для поиска
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_notes_search 
                    ON notes USING gin(to_tsvector('russian', title || ' ' || body))
                """)
                print("✅ База данных инициализирована")
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            raise


def init_db():
    """Инициализация БД при старте приложения."""
    Database.init_database()