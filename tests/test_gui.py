"""
Тесты для модуля gui.py
"""

import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock, Mock
from notebookk.gui import NoteApp
from notebookk.models import Note


class TestNoteApp(unittest.TestCase):
    """Тестирование графического интерфейса приложения"""

    def setUp(self):
        """Создание тестового окна"""
        # Создаем корневое окно для тестов
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем окно, чтобы оно не мешало

        # Мокаем загрузку заметок
        self.load_patcher = patch('notebookk.gui.load_notes')
        self.save_patcher = patch('notebookk.gui.save_notes')

        self.mock_load_notes = self.load_patcher.start()
        self.mock_save_notes = self.save_patcher.start()

        # Тестовые данные
        self.test_notes = [
            Note(1, "Test Note 1", "This is first test note", "todo", "medium"),
            Note(2, "Important Note", "This is very important", "in_progress", "high"),
            Note(3, "Completed Task", "This task is done", "done", "low")
        ]
        self.mock_load_notes.return_value = self.test_notes.copy()

    def tearDown(self):
        """Очистка после тестов"""
        self.load_patcher.stop()
        self.save_patcher.stop()
        self.root.destroy()

    def test_app_initialization(self):
        """Тест инициализации приложения"""
        # Отключаем trace события чтобы избежать ошибок во время инициализации
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Проверяем что атрибуты установлены
        self.assertEqual(app.notes, self.test_notes)
        self.assertEqual(app.next_id, 4)  # Максимальный ID + 1

        # Проверяем что интерфейс построен
        self.assertTrue(hasattr(app, 'title_entry'))
        self.assertTrue(hasattr(app, 'body_text'))
        self.assertTrue(hasattr(app, 'tree'))

        # Проверяем заголовок окна
        self.assertIn("Менеджер заметок", self.root.title())

    def test_add_note_valid(self):
        """Тест добавления валидной заметки"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Заполняем форму
        app.title_entry.insert(0, "New Test Note")
        app.body_text.insert("1.0", "This is a new test note body")
        app.status_var.set("in_progress")
        app.priority_var.set("high")

        # Мокаем messagebox чтобы не показывать реальные окна
        with patch('notebookk.gui.messagebox') as mock_messagebox:
            # Вызываем метод добавления заметки
            app.add_note()

            # Проверяем что заметка добавлена
            self.assertEqual(len(app.notes), 4)
            self.assertEqual(app.notes[-1].title, "New Test Note")
            self.assertEqual(app.notes[-1].body, "This is a new test note body")
            self.assertEqual(app.notes[-1].status, "in_progress")
            self.assertEqual(app.notes[-1].priority, "high")

            # Проверяем что save_notes был вызван
            self.mock_save_notes.assert_called_once()

            # Проверяем что было показано сообщение об успехе
            mock_messagebox.showinfo.assert_called_once()

            # Проверяем что форма очищена
            self.assertEqual(app.title_entry.get(), "")
            self.assertEqual(app.body_text.get("1.0", "end-1c"), "")

    def test_add_note_invalid_empty_title(self):
        """Тест добавления заметки с пустым заголовком"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Оставляем заголовок пустым
        app.body_text.insert("1.0", "Body text")

        with patch('notebookk.gui.messagebox') as mock_messagebox:
            app.add_note()

            # Проверяем что показано предупреждение
            mock_messagebox.showwarning.assert_called_once()
            self.assertIn("Введите заголовок", mock_messagebox.showwarning.call_args[0][1])

            # Проверяем что заметка не добавлена
            self.assertEqual(len(app.notes), 3)
            self.mock_save_notes.assert_not_called()

    def test_add_note_invalid_empty_body(self):
        """Тест добавления заметки с пустым текстом"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Заполняем только заголовок
        app.title_entry.insert(0, "Title")

        with patch('notebookk.gui.messagebox') as mock_messagebox:
            app.add_note()

            # Проверяем что показано предупреждение
            mock_messagebox.showwarning.assert_called_once()
            self.assertIn("Введите текст", mock_messagebox.showwarning.call_args[0][1])

            # Проверяем что заметка не добавлена
            self.assertEqual(len(app.notes), 3)
            self.mock_save_notes.assert_not_called()

    def test_refresh_list(self):
        """Тест обновления списка заметок"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Вызываем обновление списка
        app.refresh_list()

        # Проверяем что заметки добавлены в дерево
        items = app.tree.get_children()
        self.assertEqual(len(items), 3)

        # Проверяем содержимое первой заметки
        first_item = app.tree.item(items[0])
        self.assertEqual(first_item['values'][0], 1)  # ID
        self.assertEqual(first_item['values'][1], "Test Note 1")  # Заголовок
        self.assertEqual(first_item['values'][2], "todo")  # Статус
        self.assertEqual(first_item['values'][3], "medium")  # Приоритет

    def test_refresh_list_with_search_filter(self):
        """Тест обновления списка с фильтром поиска"""
        # Отключаем trace события при инициализации
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Теперь устанавливаем поисковый запрос и обновляем список
        app.search_var.set("important")
        app.refresh_list()

        # Проверяем что отфильтрована только одна заметка
        items = app.tree.get_children()
        self.assertEqual(len(items), 1)

        # Проверяем что это правильная заметка
        first_item = app.tree.item(items[0])
        self.assertEqual(first_item['values'][1], "Important Note")

    def test_refresh_list_with_status_filter(self):
        """Тест обновления списка с фильтром по статусу"""
        # Отключаем trace события при инициализации
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Устанавливаем фильтр по статусу
        app.filter_status.set("done")
        app.refresh_list()

        # Проверяем что отфильтрована только одна заметка
        items = app.tree.get_children()
        self.assertEqual(len(items), 1)

        # Проверяем что это правильная заметка
        first_item = app.tree.item(items[0])
        self.assertEqual(first_item['values'][2], "done")

    def test_refresh_list_with_priority_filter(self):
        """Тест обновления списка с фильтром по приоритету"""
        # Отключаем trace события при инициализации
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Устанавливаем фильтр по приоритету
        app.filter_priority.set("high")
        app.refresh_list()

        # Проверяем что отфильтрована только одна заметка
        items = app.tree.get_children()
        self.assertEqual(len(items), 1)

        # Проверяем что это правильная заметка
        first_item = app.tree.item(items[0])
        self.assertEqual(first_item['values'][3], "high")

    def test_refresh_list_with_multiple_filters(self):
        """Тест обновления списка с несколькими фильтрами"""
        # Отключаем trace события при инициализации
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Устанавливаем несколько фильтров
        app.search_var.set("test")
        app.filter_status.set("todo")
        app.filter_priority.set("medium")
        app.refresh_list()

        # Проверяем что отфильтрована только одна заметка
        items = app.tree.get_children()
        self.assertEqual(len(items), 1)

        # Проверяем что это правильная заметка
        first_item = app.tree.item(items[0])
        self.assertEqual(first_item['values'][1], "Test Note 1")
        self.assertEqual(first_item['values'][2], "todo")
        self.assertEqual(first_item['values'][3], "medium")

    def test_delete_note(self):
        """Тест удаления заметки"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Добавляем заметку в дерево для выбора
        app.refresh_list()
        items = app.tree.get_children()

        # Выбираем первую заметку
        app.tree.selection_set(items[0])

        with patch('notebookk.gui.messagebox') as mock_messagebox:
            # Мокаем askyesno чтобы вернуть True (подтверждение удаления)
            mock_messagebox.askyesno.return_value = True

            # Вызываем удаление
            app.delete_note()

            # Проверяем что заметка удалена
            self.assertEqual(len(app.notes), 2)

            # Проверяем что save_notes был вызван
            self.mock_save_notes.assert_called_once()

            # Проверяем что было показано сообщение об успехе
            mock_messagebox.showinfo.assert_called_once()

            # Проверяем подтверждение удаления
            mock_messagebox.askyesno.assert_called_once()

    def test_delete_note_no_selection(self):
        """Тест удаления без выбора заметки"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        with patch('notebookk.gui.messagebox') as mock_messagebox:
            # Вызываем удаление без выбора
            app.delete_note()

            # Проверяем что показано предупреждение
            mock_messagebox.showwarning.assert_called_once()
            self.assertIn("Выберите заметку", mock_messagebox.showwarning.call_args[0][1])

            # Проверяем что заметки не удалены
            self.assertEqual(len(app.notes), 3)
            self.mock_save_notes.assert_not_called()

    def test_delete_note_cancelled(self):
        """Тест отмены удаления заметки"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Добавляем заметку в дерево для выбора
        app.refresh_list()
        items = app.tree.get_children()

        # Выбираем первую заметку
        app.tree.selection_set(items[0])

        with patch('notebookk.gui.messagebox') as mock_messagebox:
            # Мокаем askyesno чтобы вернуть False (отмена удаления)
            mock_messagebox.askyesno.return_value = False

            # Вызываем удаление
            app.delete_note()

            # Проверяем что заметка НЕ удалена
            self.assertEqual(len(app.notes), 3)

            # Проверяем что save_notes НЕ был вызван
            self.mock_save_notes.assert_not_called()

    def test_show_full_note(self):
        """Тест просмотра полной заметки"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Добавляем заметку в дерево
        app.refresh_list()
        items = app.tree.get_children()

        # Создаем событие двойного клика
        event = Mock()

        # Выбираем первую заметку
        app.tree.selection_set(items[0])

        # Мокаем создание Toplevel окна
        with patch('notebookk.gui.tk.Toplevel') as mock_toplevel:
            mock_window = MagicMock()
            mock_toplevel.return_value = mock_window

            # Вызываем просмотр заметки
            app.show_full_note(event)

            # Проверяем что окно было создано
            mock_toplevel.assert_called_once()

            # Проверяем что окно настроено
            self.assertIn("Заметка #1", mock_window.title.call_args[0][0])

    def test_copy_to_clipboard(self):
        """Тест копирования в буфер обмена"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        test_text = "Test text to copy"

        with patch('notebookk.gui.messagebox') as mock_messagebox:
            # Вызываем копирование
            app.copy_to_clipboard(test_text)

            # Проверяем что текст скопирован в буфер обмена
            self.assertEqual(app.root.clipboard_get(), test_text)

            # Проверяем что показано сообщение об успехе
            mock_messagebox.showinfo.assert_called_once()

    def test_center_window(self):
        """Тест центрирования окна"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Мокаем методы окна
        app.root.update_idletasks = MagicMock()
        app.root.winfo_width = MagicMock(return_value=800)
        app.root.winfo_height = MagicMock(return_value=600)
        app.root.winfo_screenwidth = MagicMock(return_value=1920)
        app.root.winfo_screenheight = MagicMock(return_value=1080)
        app.root.geometry = MagicMock()

        # Вызываем центрирование
        app.center_window()

        # Проверяем что окно было центрировано
        app.root.geometry.assert_called_once()
        call_args = app.root.geometry.call_args[0][0]
        self.assertIn("+560+240", call_args)  # Примерные координаты центрирования

    def test_next_id_calculation(self):
        """Тест расчета следующего ID"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Проверяем что next_id рассчитан правильно
        self.assertEqual(app.next_id, 4)  # Максимальный ID (3) + 1

        # Тестируем с пустым списком
        self.mock_load_notes.return_value = []

        # Отключаем trace события для второго приложения
        with patch.object(tk.StringVar, 'trace'):
            app2 = NoteApp(tk.Tk())

        self.assertEqual(app2.next_id, 1)  # Для пустого списка должен быть 1

        app2.root.destroy()

    def test_build_ui_creates_all_widgets(self):
        """Тест что build_ui создает все необходимые виджеты"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Проверяем что все основные виджеты созданы
        self.assertIsNotNone(app.title_entry)
        self.assertIsNotNone(app.body_text)
        self.assertIsNotNone(app.status_var)
        self.assertIsNotNone(app.priority_var)
        self.assertIsNotNone(app.search_var)
        self.assertIsNotNone(app.filter_status)
        self.assertIsNotNone(app.filter_priority)
        self.assertIsNotNone(app.tree)

    def test_empty_notes_list(self):
        """Тест работы с пустым списком заметок"""
        # Устанавливаем пустой список заметок
        self.mock_load_notes.return_value = []

        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Проверяем что next_id = 1 для пустого списка
        self.assertEqual(app.next_id, 1)

        # Проверяем что дерево пустое
        app.refresh_list()
        items = app.tree.get_children()
        self.assertEqual(len(items), 0)

    def test_note_with_special_characters(self):
        """Тест заметки со специальными символами"""
        # Отключаем trace события
        with patch.object(tk.StringVar, 'trace'):
            app = NoteApp(self.root)

        # Добавляем заметку со специальными символами
        app.title_entry.insert(0, "Note with \n newline & \"quotes\"")
        app.body_text.insert("1.0", "Body with \t tab and special chars: @#$%^&*()")
        app.status_var.set("todo")
        app.priority_var.set("medium")

        with patch('notebookk.gui.messagebox'):
            app.add_note()

            # Проверяем что заметка добавлена
            self.assertEqual(len(app.notes), 4)
            self.assertEqual(app.notes[-1].title, "Note with \n newline & \"quotes\"")
            self.assertEqual(app.notes[-1].body, "Body with \t tab and special chars: @#$%^&*()")


if __name__ == "__main__":
    unittest.main()