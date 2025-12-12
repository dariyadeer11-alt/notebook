"""Пакет notebookk - Менеджер заметок с CLI и GUI интерфейсами."""

from .main import main
from .gui import NoteApp
# Исправленный импорт: функция теперь называется delete_note_cli
from .commands import add_note, list_notes, search_notes_cli as search_notes, delete_note_cli as delete_note
from notebookk.database import init_db

__all__ = ['main', 'NoteApp', 'add_note', 'list_notes', 'search_notes', 'delete_note', 'init_db']
__version__ = '1.0.0'
__author__ = 'Notebookk Team'