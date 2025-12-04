"""
Модуль для работы с хранением данных.

Обеспечивает загрузку и сохранение заметок в JSON файл.
Использует стандартный модуль json для сериализации данных.
"""

import json
import os
from .models import Note

# Путь к файлу хранения данных
FILE_PATH = "notes.json"


def load_notes():
    """
    Загружает заметки из JSON файла.

    Returns:
        list[Note]: Список объектов Note, загруженных из файла.
        Если файл не существует или поврежден, возвращает пустой список.

    Raises:
        json.JSONDecodeError: Если файл содержит некорректный JSON
        OSError: Если возникают проблемы с доступом к файлу
    """
    if not os.path.exists(FILE_PATH):
        return []  # Файл не существует - возвращаем пустой список

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)  # Загружаем JSON в список словарей
            # Преобразуем каждый словарь в объект Note
            return [Note.from_dict(item) for item in data]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"⚠️ Ошибка чтения файла {FILE_PATH}: {e}")
        return []  # Возвращаем пустой список при ошибке
    except Exception as e:
        print(f"⚠️ Неожиданная ошибка при загрузке заметок: {e}")
        return []


def save_notes(notes):
    """
    Сохраняет список заметок в JSON файл.

    Args:
        notes (list[Note]): Список объектов Note для сохранения

    Raises:
        OSError: Если возникают проблемы с записью в файл
        TypeError: Если объекты нельзя сериализовать в JSON
    """
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            # Преобразуем каждую заметку в словарь и сохраняем
            json.dump(
                [note.to_dict() for note in notes],
                f,
                indent=4,  # Форматирование с отступами
                ensure_ascii=False,  # Поддержка кириллицы
                sort_keys=True  # Сортировка ключей для читаемости
            )
    except Exception as e:
        print(f"❌ Ошибка сохранения заметок: {e}")
        raise