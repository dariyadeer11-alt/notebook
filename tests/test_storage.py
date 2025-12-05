"""
Тесты для модуля storage.py
"""

import unittest
import json
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from notebookk.storage import load_notes, save_notes
from notebookk.models import Note


class TestStorage(unittest.TestCase):
    """Тестирование модуля хранения данных"""

    def setUp(self):
        """Создание временного файла для тестов"""
        # Создаем временную директорию
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, "test_notes.json")

        # Патчим FILE_PATH чтобы использовать наш временный файл
        self.file_patcher = patch('notebookk.storage.FILE_PATH', self.test_file)
        self.file_patcher.start()

        # Тестовые данные
        self.test_notes = [
            Note(1, "Note 1", "Body 1", "todo", "medium"),
            Note(2, "Note 2", "Body 2", "done", "high")
        ]

    def tearDown(self):
        """Очистка после тестов"""
        self.file_patcher.stop()
        self.temp_dir.cleanup()

    def test_load_notes_file_not_exists(self):
        """Тест загрузки при отсутствии файла"""
        # Убедимся, что файла нет
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        notes = load_notes()
        self.assertEqual(notes, [])
        self.assertIsInstance(notes, list)

    def test_save_and_load_notes(self):
        """Тест сохранения и загрузки заметок"""
        # Сохраняем заметки
        save_notes(self.test_notes)

        # Проверяем что файл создан
        self.assertTrue(os.path.exists(self.test_file))

        # Загружаем заметки
        loaded_notes = load_notes()

        # Проверяем что загружено правильное количество
        self.assertEqual(len(loaded_notes), 2)

        # Проверяем содержимое
        self.assertEqual(loaded_notes[0].id, 1)
        self.assertEqual(loaded_notes[0].title, "Note 1")
        self.assertEqual(loaded_notes[1].id, 2)
        self.assertEqual(loaded_notes[1].status, "done")

    def test_load_notes_invalid_json(self):
        """Тест загрузки при поврежденном JSON"""
        # Создаем файл с некорректным JSON
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("invalid json {")

        # Должен вернуть пустой список
        notes = load_notes()
        self.assertEqual(notes, [])

    def test_load_notes_missing_keys(self):
        """Тест загрузки JSON с отсутствующими ключами"""
        # Создаем JSON без обязательных полей
        invalid_data = [{"id": 1, "title": "Test"}]  # Нет body

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(invalid_data, f)

        # Должен вернуть пустой список (будет KeyError)
        notes = load_notes()
        self.assertEqual(notes, [])

    def test_save_notes_empty_list(self):
        """Тест сохранения пустого списка"""
        save_notes([])

        # Проверяем что файл создан
        self.assertTrue(os.path.exists(self.test_file))

        # Загружаем и проверяем
        loaded_notes = load_notes()
        self.assertEqual(loaded_notes, [])

    def test_save_notes_unicode_support(self):
        """Тест поддержки Unicode (кириллицы)"""
        note_with_unicode = Note(1, "Заголовок", "Текст на русском", "todo", "medium")

        save_notes([note_with_unicode])

        # Проверяем что файл создан
        self.assertTrue(os.path.exists(self.test_file))

        # Читаем файл и проверяем кодировку
        with open(self.test_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Заголовок", content)
            self.assertIn("Текст на русском", content)

        # Загружаем обратно
        loaded_notes = load_notes()
        self.assertEqual(len(loaded_notes), 1)
        self.assertEqual(loaded_notes[0].title, "Заголовок")

    def test_save_notes_permission_error(self):
        """Тест обработки ошибки записи в файл"""
        # Создаем директорию без прав на запись
        read_only_dir = os.path.join(self.temp_dir.name, "readonly")
        os.makedirs(read_only_dir, exist_ok=True)
        read_only_file = os.path.join(read_only_dir, "notes.json")

        # Меняем FILE_PATH на файл в read-only директории
        self.file_patcher.stop()  # Останавливаем текущий патч
        self.file_patcher = patch('notebookk.storage.FILE_PATH', read_only_file)
        self.file_patcher.start()

        # Делаем директорию read-only (только для Unix, для Windows нужен другой подход)
        if os.name != 'nt':  # Не Windows
            import stat
            os.chmod(read_only_dir, stat.S_IRUSR | stat.S_IXUSR)  # Только чтение и выполнение

            # Должна возникнуть ошибка при сохранении
            with self.assertRaises(OSError):
                save_notes(self.test_notes)

            # Восстанавливаем права
            os.chmod(read_only_dir, stat.S_IRWXU)
        else:
            # Для Windows просто пропускаем этот тест
            self.skipTest("Проверка прав доступа на Windows требует особого подхода")

    def test_file_format_pretty_print(self):
        """Тест форматирования JSON файла"""
        save_notes(self.test_notes)

        # Проверяем что файл создан
        self.assertTrue(os.path.exists(self.test_file))

        with open(self.test_file, "r", encoding="utf-8") as f:
            content = f.read()

            # Проверяем форматирование
            lines = content.strip().split('\n')
            self.assertTrue(len(lines) > 1)  # Должен быть многострочный JSON

            # Проверяем наличие отступов
            self.assertTrue(any('    ' in line for line in lines))

            # Проверяем что JSON валиден
            parsed = json.loads(content)
            self.assertEqual(len(parsed), 2)
            self.assertEqual(parsed[0]["id"], 1)

    def test_load_notes_with_valid_json(self):
        """Тест загрузки с валидным JSON"""
        # Создаем валидный JSON файл
        valid_data = [
            {
                "id": 10,
                "title": "Valid Note",
                "body": "Valid body",
                "status": "in_progress",
                "priority": "high",
                "created": "2023-12-01 10:30"
            }
        ]

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(valid_data, f)

        notes = load_notes()

        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].id, 10)
        self.assertEqual(notes[0].title, "Valid Note")
        self.assertEqual(notes[0].status, "in_progress")
        self.assertEqual(notes[0].created, "2023-12-01 10:30")

    def test_save_notes_overwrites_file(self):
        """Тест что save_notes перезаписывает файл"""
        # Сначала сохраняем одни заметки
        save_notes(self.test_notes)

        # Проверяем что файл содержит 2 заметки
        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)

        # Теперь сохраняем другие заметки
        new_notes = [Note(99, "New Note", "New Body")]
        save_notes(new_notes)

        # Проверяем что файл обновился
        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["id"], 99)
            self.assertEqual(data[0]["title"], "New Note")

    def test_load_notes_handles_exceptions(self):
        """Тест обработки исключений при загрузке"""
        # Создаем пустой файл (не валидный JSON)
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("")

        notes = load_notes()
        self.assertEqual(notes, [])  # Должен вернуть пустой список

    def test_save_notes_with_special_characters(self):
        """Тест сохранения заметок со специальными символами"""
        note_with_special_chars = Note(
            1,
            "Title with \n newline & \"quotes\"",
            "Body with \t tab and \r carriage return",
            "todo",
            "medium"
        )

        save_notes([note_with_special_chars])

        # Проверяем что файл создан и может быть загружен
        notes = load_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Title with \n newline & \"quotes\"")
        self.assertEqual(notes[0].body, "Body with \t tab and \r carriage return")

    def test_ensure_ascii_false(self):
        """Тест что ensure_ascii=False сохраняет Unicode как есть"""
        note = Note(1, "Тест", "Русский текст", "todo", "medium")

        save_notes([note])

        # Читаем файл как байты чтобы убедиться в отсутствии escape-последовательностей
        with open(self.test_file, "rb") as f:
            content_bytes = f.read()
            content_str = content_bytes.decode('utf-8')

            # Проверяем что русские символы сохранены как есть (не как \uXXXX)
            self.assertIn("Тест", content_str)
            self.assertIn("Русский", content_str)
            self.assertNotIn("\\u", content_str)  # Не должно быть Unicode escape


if __name__ == "__main__":
    unittest.main()