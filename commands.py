# notebookk/commands.py
import argparse
from .storage import load_notes, save_notes
from .models import Note
import sys


def get_next_id(notes):
    """Получить следующий ID для новой заметки"""
    if not notes:
        return 1
    return max(note.id for note in notes) + 1


def add_note(args):
    """Добавить новую заметку"""
    notes = load_notes()
    new_id = get_next_id(notes)

    note = Note(
        new_id,
        args.title,
        args.body,
        args.status,
        args.priority
    )
    notes.append(note)
    save_notes(notes)

    print(f"✅ Заметка добавлена! ID: {new_id}")
    print(f"   Заголовок: {note.title}")
    print(f"   Статус: {note.status}, Приоритет: {note.priority}")
