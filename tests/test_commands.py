"""
Тесты для модуля commands.py
"""

import unittest
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from notebookk.commands import add_note, list_notes, search_notes, delete_note, get_next_id
from notebookk.models import Note


class TestCommands(unittest.TestCase):
    """Тестирование CLI команд"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.test_notes = [
            Note(1, "Test Note 1", "This is first test note", "todo", "medium"),
            Note(2, "Important Note", "This is very important", "in_progress", "high"),
            Note(3, "Completed Task", "This task is done", "done", "low")
        ]

        # Мокаем load_notes и save_notes
        self.load_patcher = patch('notebookk.commands.load_notes')
        self.save_patcher = patch('notebookk.commands.save_notes')

        self.mock_load_notes = self.load_patcher.start()
        self.mock_save_notes = self.save_patcher.start()

        self.mock_load_notes.return_value = self.test_notes.copy()

    def tearDown(self):
        """Очистка после тестов"""
        self.load_patcher.stop()
        self.save_patcher.stop()

    def test_get_next_id(self):
        """Тест генерации следующего ID"""
        # С пустым списком
        self.assertEqual(get_next_id([]), 1)

        # С непустым списком
        self.assertEqual(get_next_id(self.test_notes), 4)

        # С несортированными ID
        notes_unsorted = [Note(5, "Test", "Body"), Note(1, "Test", "Body")]
        self.assertEqual(get_next_id(notes_unsorted), 6)

    def test_add_note(self):
        """Тест добавления заметки"""
        # Создаем мок аргументов
        mock_args = MagicMock()
        mock_args.title = "New Test Note"
        mock_args.body = "This is a new test note body"
        mock_args.status = "in_progress"
        mock_args.priority = "high"

        # Перенаправляем stdout для захвата вывода
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            add_note(mock_args)

            # Проверяем что save_notes был вызван
            self.mock_save_notes.assert_called_once()

            # Проверяем вывод
            output = captured_output.getvalue()
            self.assertIn("✅ Заметка добавлена! ID: 4", output)
            self.assertIn("Заголовок: New Test Note", output)
            self.assertIn("Статус: in_progress", output)
            self.assertIn("Приоритет: high", output)

        finally:
            sys.stdout = sys.__stdout__

    def test_list_notes_no_filter(self):
        """Тест вывода списка без фильтров"""
        mock_args = MagicMock()
        mock_args.status = None
        mock_args.priority = None

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            list_notes(mock_args)

            output = captured_output.getvalue()
            self.assertIn("📋 Всего заметок: 3", output)
            self.assertIn("Test Note 1", output)
            self.assertIn("Important Note", output)
            self.assertIn("Completed Task", output)

        finally:
            sys.stdout = sys.__stdout__

    def test_list_notes_with_status_filter(self):
        """Тест вывода списка с фильтром по статусу"""
        mock_args = MagicMock()
        mock_args.status = "done"
        mock_args.priority = None

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            list_notes(mock_args)

            output = captured_output.getvalue()
            self.assertIn("Фильтр по статусу: done", output)
            self.assertIn("Completed Task", output)
            # Не должно быть заметок с другим статусом
            self.assertNotIn("Test Note 1", output)

        finally:
            sys.stdout = sys.__stdout__

    def test_list_notes_with_priority_filter(self):
        """Тест вывода списка с фильтром по приоритету"""
        mock_args = MagicMock()
        mock_args.status = None
        mock_args.priority = "high"

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            list_notes(mock_args)

            output = captured_output.getvalue()
            self.assertIn("Фильтр по приоритету: high", output)
            self.assertIn("Important Note", output)
            # Приоритет low - не должно быть
            self.assertNotIn("Completed Task", output)

        finally:
            sys.stdout = sys.__stdout__

    def test_list_notes_empty(self):
        """Тест вывода пустого списка"""
        self.mock_load_notes.return_value = []

        mock_args = MagicMock()
        mock_args.status = None
        mock_args.priority = None

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            list_notes(mock_args)

            output = captured_output.getvalue()
            self.assertIn("📝 Заметки не найдены", output)

        finally:
            sys.stdout = sys.__stdout__

    def test_search_notes_found(self):
        """Тест поиска заметок (найдены результаты)"""
        mock_args = MagicMock()
        mock_args.keyword = "important"

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            search_notes(mock_args)

            output = captured_output.getvalue()
            # Проверяем общее сообщение
            self.assertIn("🔍 Найдено 1 заметок по запросу 'important':", output)
            # Проверяем заголовок заметки
            self.assertIn("Important Note", output)
            # Проверяем что ключевое слово упоминается (без учета ANSI кодов)
            # Ищем "important" без escape-последовательностей
            cleaned_output = output.replace('\x1b[1;33m', '').replace('\x1b[0m', '')
            self.assertIn("important", cleaned_output.lower())

        finally:
            sys.stdout = sys.__stdout__

    def test_search_notes_not_found(self):
        """Тест поиска заметок (ничего не найдено)"""
        mock_args = MagicMock()
        mock_args.keyword = "nonexistent"

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            search_notes(mock_args)

            output = captured_output.getvalue()
            self.assertIn(f"🔍 По запросу 'nonexistent' ничего не найдено", output)

        finally:
            sys.stdout = sys.__stdout__

    def test_search_notes_case_insensitive(self):
        """Тест регистронезависимого поиска"""
        mock_args = MagicMock()
        mock_args.keyword = "TEST"  # В верхнем регистре

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            search_notes(mock_args)

            output = captured_output.getvalue()
            # Должен найти несмотря на регистр
            cleaned_output = output.replace('\x1b[1;33m', '').replace('\x1b[0m', '')
            self.assertIn("test note 1", cleaned_output.lower())

        finally:
            sys.stdout = sys.__stdout__

    def test_search_notes_in_title_only(self):
        """Тест поиска по заголовку (слово не в тексте)"""
        # Создаем заметку, где ключевое слово только в заголовке
        notes_with_title_keyword = [
            Note(1, "Special Title", "Regular body text", "todo", "medium")
        ]
        self.mock_load_notes.return_value = notes_with_title_keyword

        mock_args = MagicMock()
        mock_args.keyword = "special"

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            search_notes(mock_args)

            output = captured_output.getvalue()
            self.assertIn("🔍 Найдено 1 заметок по запросу 'special':", output)
            self.assertIn("Special Title", output)
            # Должен показать начало текста (первые 100 символов)
            self.assertIn("Regular body text", output)

        finally:
            sys.stdout = sys.__stdout__

    def test_delete_note_success(self):
        """Тест успешного удаления заметки"""
        mock_args = MagicMock()
        mock_args.id = 2

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            delete_note(mock_args)

            output = captured_output.getvalue()
            self.assertIn("🗑️  Заметка с ID 2 удалена", output)
            self.mock_save_notes.assert_called_once()

        finally:
            sys.stdout = sys.__stdout__

    def test_delete_note_not_found(self):
        """Тест удаления несуществующей заметки"""
        mock_args = MagicMock()
        mock_args.id = 999

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            delete_note(mock_args)

            output = captured_output.getvalue()
            self.assertIn("❌ Заметка с ID 999 не найдена", output)
            self.assertIn("Доступные ID:", output)
            self.mock_save_notes.assert_not_called()

        finally:
            sys.stdout = sys.__stdout__

    def test_delete_note_last_note(self):
        """Тест удаления последней заметки"""
        # Создаем список с одной заметкой
        single_note = [Note(1, "Single", "Note")]
        self.mock_load_notes.return_value = single_note

        mock_args = MagicMock()
        mock_args.id = 1

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            delete_note(mock_args)

            output = captured_output.getvalue()
            self.assertIn("🗑️  Заметка с ID 1 удалена", output)
            # Проверяем что save_notes вызван с пустым списком
            self.mock_save_notes.assert_called_once()
            call_args = self.mock_save_notes.call_args[0][0]
            self.assertEqual(len(call_args), 0)

        finally:
            sys.stdout = sys.__stdout__

    def test_search_notes_multiple_results(self):
        """Тест поиска с несколькими результатами"""
        # Добавляем еще одну заметку с тем же ключевым словом
        extra_note = Note(4, "Another important thing", "This is also important", "todo", "medium")
        self.mock_load_notes.return_value = self.test_notes + [extra_note]

        mock_args = MagicMock()
        mock_args.keyword = "important"

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            search_notes(mock_args)

            output = captured_output.getvalue()
            self.assertIn("🔍 Найдено 2 заметок по запросу 'important':", output)
            self.assertIn("Important Note", output)
            self.assertIn("Another important thing", output)

        finally:
            sys.stdout = sys.__stdout__

    def test_search_notes_empty_keyword(self):
        """Тест поиска с пустым ключевым словом"""
        mock_args = MagicMock()
        mock_args.keyword = ""

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            search_notes(mock_args)

            output = captured_output.getvalue()
            # Пустой запрос должен найти все заметки
            self.assertIn("🔍 Найдено 3 заметок по запросу '':", output)

        finally:
            sys.stdout = sys.__stdout__

    def test_list_notes_with_both_filters(self):
        """Тест вывода списка с обоими фильтрами"""
        mock_args = MagicMock()
        mock_args.status = "in_progress"
        mock_args.priority = "high"

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            list_notes(mock_args)

            output = captured_output.getvalue()
            self.assertIn("Фильтр по статусу: in_progress", output)
            self.assertIn("Фильтр по приоритету: high", output)
            # Должна быть только одна заметка, соответствующая обоим фильтрам
            self.assertIn("Important Note", output)
            self.assertNotIn("Test Note 1", output)
            self.assertNotIn("Completed Task", output)

        finally:
            sys.stdout = sys.__stdout__

    def test_add_note_default_values(self):
        """Тест добавления заметки со значениями по умолчанию"""
        mock_args = MagicMock()
        mock_args.title = "Default Note"
        mock_args.body = "Default body"
        mock_args.status = "todo"  # Значения по умолчанию
        mock_args.priority = "medium"

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            add_note(mock_args)

            output = captured_output.getvalue()
            self.assertIn("✅ Заметка добавлена!", output)
            self.assertIn("Статус: todo", output)
            self.assertIn("Приоритет: medium", output)

        finally:
            sys.stdout = sys.__stdout__


if __name__ == "__main__":
    unittest.main()