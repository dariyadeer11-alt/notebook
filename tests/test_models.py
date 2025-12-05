"""
Тесты для модуля models.py
"""

import unittest
import json
from datetime import datetime
from notebookk.models import Note


class TestNote(unittest.TestCase):
    """Тестирование класса Note"""

    def setUp(self):
        """Подготовка тестового объекта Note"""
        self.note = Note(1, "Test Title", "Test Body", "todo", "medium")

    def test_note_creation(self):
        """Тест создания заметки"""
        self.assertEqual(self.note.id, 1)
        self.assertEqual(self.note.title, "Test Title")
        self.assertEqual(self.note.body, "Test Body")
        self.assertEqual(self.note.status, "todo")
        self.assertEqual(self.note.priority, "medium")
        self.assertIsInstance(self.note.created, str)

        # Проверяем формат даты
        try:
            datetime.strptime(self.note.created, "%Y-%m-%d %H:%M")
        except ValueError:
            self.fail("Неверный формат даты в created")

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        note_dict = self.note.to_dict()

        self.assertEqual(note_dict["id"], 1)
        self.assertEqual(note_dict["title"], "Test Title")
        self.assertEqual(note_dict["body"], "Test Body")
        self.assertEqual(note_dict["status"], "todo")
        self.assertEqual(note_dict["priority"], "medium")
        self.assertEqual(note_dict["created"], self.note.created)

        # Проверяем, что все ключи присутствуют
        expected_keys = {"id", "title", "body", "status", "priority", "created"}
        self.assertEqual(set(note_dict.keys()), expected_keys)

    def test_from_dict(self):
        """Тест создания объекта из словаря"""
        data = {
            "id": 2,
            "title": "From Dict",
            "body": "Body from dict",
            "status": "done",
            "priority": "high",
            "created": "2023-12-01 10:30"
        }

        note = Note.from_dict(data)

        self.assertEqual(note.id, 2)
        self.assertEqual(note.title, "From Dict")
        self.assertEqual(note.body, "Body from dict")
        self.assertEqual(note.status, "done")
        self.assertEqual(note.priority, "high")
        self.assertEqual(note.created, "2023-12-01 10:30")

    def test_from_dict_with_defaults(self):
        """Тест создания из словаря с отсутствующими значениями"""
        data = {
            "id": 3,
            "title": "Minimal",
            "body": "Minimal body"
        }

        note = Note.from_dict(data)

        self.assertEqual(note.id, 3)
        self.assertEqual(note.title, "Minimal")
        self.assertEqual(note.body, "Minimal body")
        self.assertEqual(note.status, "todo")  # Значение по умолчанию
        self.assertEqual(note.priority, "medium")  # Значение по умолчанию
        self.assertIsNotNone(note.created)  # Должна быть установлена текущая дата

    def test_repr(self):
        """Тест строкового представления"""
        repr_str = repr(self.note)
        self.assertIn("Note", repr_str)
        self.assertIn("id=1", repr_str)
        self.assertIn("title='Test Title'", repr_str)
        self.assertIn("status='todo'", repr_str)

    def test_note_with_different_status_and_priority(self):
        """Тест создания заметок с разными статусами и приоритетами"""
        statuses = ["todo", "in_progress", "done"]
        priorities = ["low", "medium", "high"]

        for status in statuses:
            for priority in priorities:
                note = Note(99, "Test", "Body", status, priority)
                self.assertEqual(note.status, status)
                self.assertEqual(note.priority, priority)


if __name__ == "__main__":
    unittest.main()