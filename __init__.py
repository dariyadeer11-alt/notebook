"""
Пакет notebookk - Менеджер заметок с CLI и GUI интерфейсами.

Основные экспортируемые компоненты:
- main: Основная точка входа приложения
- NoteApp: Класс графического интерфейса
- Функции для работы с заметками: add_note, list_notes, search_notes, delete_note
"""

from .main import main
from .gui import NoteApp
from .commands import add_note, list_notes, search_notes, delete_note

__all__ = ['main', 'NoteApp', 'add_note', 'list_notes', 'search_notes', 'delete_note']
__version__ = '1.0.0'
__author__ = 'Notebookk Team'