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

def list_notes(args):
    """Показать список заметок"""
    notes = load_notes()
    filtered = notes

    # Фильтрация по статусу
    if args.status:
        filtered = [n for n in filtered if n.status == args.status]

    # Фильтрация по приоритету
    if args.priority:
        filtered = [n for n in filtered if n.priority == args.priority]

    if not filtered:
        print("📝 Заметки не найдены")
        return

    print(f"📋 Всего заметок: {len(filtered)}")
    print("-" * 80)
    for note in filtered:
        print(f"ID: {note.id:3d} | {note.title:<30} | {note.status:10} | {note.priority:7} | {note.created}")
    print("-" * 80)


def search_notes(args):
    """Поиск заметок по ключевому слову"""
    notes = load_notes()
    keyword = args.keyword.lower()
    found = []

    for note in notes:
        if keyword in note.title.lower() or keyword in note.body.lower():
            found.append(note)

    if not found:
        print(f"🔍 По слову '{args.keyword}' ничего не найдено")
        return

    print(f"🔍 Найдено {len(found)} заметок по запросу '{args.keyword}':")
    print("-" * 80)
    for note in found:
        print(f"ID: {note.id:3d} | {note.title:<30} | {note.status:10} | {note.priority:7}")
        print(f"   {note.body[:100]}{'...' if len(note.body) > 100 else ''}")
        print("-" * 80)


def delete_note(args):
    """Удалить заметку по ID"""
    notes = load_notes()
    original_count = len(notes)

    notes = [n for n in notes if n.id != args.id]

    if len(notes) == original_count:
        print(f"❌ Заметка с ID {args.id} не найдена")
        return

    save_notes(notes)
    print(f"🗑️  Заметка с ID {args.id} удалена")