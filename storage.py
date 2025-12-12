"""
storage.py
Модуль для работы с хранением данных в PostgreSQL.
"""

from notebookk.database import Database
from .models import Note
import psycopg2


def load_notes():
    """
    Загружает заметки из базы данных.

    Returns:
        list[Note]: Список объектов Note, загруженных из БД.
        Если таблица не существует, возвращает пустой список.
    """
    try:
        with Database.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, title, body, status, priority, 
                       TO_CHAR(created, 'YYYY-MM-DD HH24:MI') as created
                FROM notes 
                ORDER BY created DESC
            """)
            notes_data = cursor.fetchall()

            # Преобразуем словари в объекты Note
            notes = []
            for data in notes_data:
                note = Note(
                    data['id'],
                    data['title'],
                    data['body'],
                    data['status'],
                    data['priority']
                )
                note.created = data['created']
                notes.append(note)

            return notes

    except psycopg2.Error as e:
        print(f"⚠️ Ошибка чтения из БД: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Неожиданная ошибка при загрузке заметок: {e}")
        return []


def save_notes(notes):
    """
    Сохраняет все заметки в базу данных.
    ВАЖНО: Этот метод перезаписывает все записи в БД.
    Используется для синхронизации при удалении/изменении из GUI.

    Args:
        notes (list[Note]): Список объектов Note для сохранения
    """
    try:
        with Database.get_cursor() as cursor:
            # Очищаем таблицу
            cursor.execute("DELETE FROM notes")

            # Вставляем все заметки
            for note in notes:
                cursor.execute("""
                    INSERT INTO notes (id, title, body, status, priority, created)
                    VALUES (%s, %s, %s, %s, %s, %s::timestamp)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        body = EXCLUDED.body,
                        status = EXCLUDED.status,
                        priority = EXCLUDED.priority,
                        updated = CURRENT_TIMESTAMP
                """, (
                    note.id,
                    note.title,
                    note.body,
                    note.status,
                    note.priority,
                    note.created
                ))

    except Exception as e:
        print(f"❌ Ошибка сохранения заметок: {e}")
        raise


def save_note(note):
    """
    Сохраняет одну заметку в БД.

    Args:
        note (Note): Объект заметки для сохранения
    """
    try:
        with Database.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO notes (title, body, status, priority)
                VALUES (%s, %s, %s, %s)
                RETURNING id, TO_CHAR(created, 'YYYY-MM-DD HH24:MI') as created
            """, (
                note.title,
                note.body,
                note.status,
                note.priority
            ))

            result = cursor.fetchone()
            note.id = result['id']
            note.created = result['created']

    except Exception as e:
        print(f"❌ Ошибка сохранения заметки: {e}")
        raise

def update_note(note):
    """
    Обновляет существующую заметку в БД.

    Args:
        note (Note): Объект заметки для обновления
    """
    try:
        with Database.get_cursor() as cursor:
            cursor.execute("""
                UPDATE notes 
                SET title = %s, 
                    body = %s, 
                    status = %s, 
                    priority = %s,
                    updated = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                note.title,
                note.body,
                note.status,
                note.priority,
                note.id
            ))

    except Exception as e:
        print(f"❌ Ошибка обновления заметки: {e}")
        raise


def delete_note_by_id(note_id):
    """
    Удаляет заметку по ID.

    Args:
        note_id (int): ID заметки для удаления
    """
    try:
        with Database.get_cursor() as cursor:
            cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))

    except Exception as e:
        print(f"❌ Ошибка удаления заметки: {e}")
        raise

def search_notes(keyword):
    """
    Ищет заметки по ключевому слову.

    Args:
        keyword (str): Ключевое слово для поиска

    Returns:
        list[Note]: Список найденных заметок
    """
    try:
        with Database.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, title, body, status, priority, 
                       TO_CHAR(created, 'YYYY-MM-DD HH24:MI') as created
                FROM notes 
                WHERE title ILIKE %s OR body ILIKE %s
                ORDER BY created DESC
            """, (f'%{keyword}%', f'%{keyword}%'))

            notes_data = cursor.fetchall()

            # Преобразуем словари в объекты Note
            notes = []
            for data in notes_data:
                note = Note(
                    data['id'],
                    data['title'],
                    data['body'],
                    data['status'],
                    data['priority']
                )
                note.created = data['created']
                notes.append(note)

            return notes

    except Exception as e:
        print(f"⚠️ Ошибка поиска заметок: {e}")
        return []

def get_note_by_id(note_id):
    """
    Получает заметку по ID.

    Args:
        note_id (int): ID заметки

    Returns:
        Note: Объект заметки или None если не найдена
    """
    try:
        with Database.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, title, body, status, priority, 
                       TO_CHAR(created, 'YYYY-MM-DD HH24:MI') as created
                FROM notes 
                WHERE id = %s
            """, (note_id,))

            data = cursor.fetchone()
            if data:
                note = Note(
                    data['id'],
                    data['title'],
                    data['body'],
                    data['status'],
                    data['priority']
                )
                note.created = data['created']
                return note
            return None

    except Exception as e:
        print(f"⚠️ Ошибка получения заметки: {e}")
        return None