"""
Модуль моделей данных приложения.

Содержит класс Note - основную модель данных для заметок.
Предоставляет методы для сериализации/десериализации в формат JSON.
"""

import datetime


class Note:
    """
    Класс, представляющий заметку в приложении.

    Attributes:
        id (int): Уникальный идентификатор заметки
        title (str): Заголовок заметки
        body (str): Текст заметки
        status (str): Статус заметки (todo/in_progress/done)
        priority (str): Приоритет заметки (low/medium/high)
        created (str): Дата и время создания в формате 'YYYY-MM-DD HH:MM'
    """

    def __init__(self, id, title, body, status="todo", priority="medium"):
        """
        Инициализирует новую заметку.

        Args:
            id (int): Уникальный идентификатор
            title (str): Заголовок заметки
            body (str): Текст заметки
            status (str): Статус заметки (default: "todo")
            priority (str): Приоритет заметки (default: "medium")
        """
        self.id = id
        self.title = title
        self.body = body
        self.status = status
        self.priority = priority
        self.created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        """
        Преобразует объект Note в словарь для сохранения в JSON.

        Returns:
            dict: Словарь с данными заметки, готовый для сериализации
        """
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "status": self.status,
            "priority": self.priority,
            "created": self.created
        }

    @staticmethod
    def from_dict(data):
        """
        Создает объект Note из словаря (при загрузке из JSON).

        Args:
            data (dict): Словарь с данными заметки

        Returns:
            Note: Восстановленный объект заметки
        """
        note = Note(
            data["id"],
            data["title"],
            data["body"],
            data.get("status", "todo"),
            data.get("priority", "medium")
        )
        note.created = data.get("created", note.created)
        return note

    def __repr__(self):
        """Строковое представление объекта для отладки."""
        return f"Note(id={self.id}, title='{self.title}', status='{self.status}')"