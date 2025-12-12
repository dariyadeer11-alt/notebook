"""
commands.py
Модуль CLI команд приложения.
"""

from .storage import load_notes, save_note, delete_note_by_id, search_notes, get_note_by_id
from .models import Note
from notebookk.database import init_db


def get_next_id(notes):
    """
    Генерирует следующий уникальный ID для новой заметки.

    Args:
        notes (list[Note]): Список существующих заметок

    Returns:
        int: Следующий доступный ID
    """
    if not notes:
        return 1
    return max(note.id for note in notes) + 1


def add_note(args):
    """
    Добавляет новую заметку с параметрами из аргументов.

    Args:
        args: Объект аргументов с полями:
            - title (str): Заголовок заметки
            - body (str): Текст заметки
            - status (str): Статус заметки
            - priority (str): Приоритет заметки

    Prints:
        Информация о добавленной заметке или сообщение об ошибке
    """
    # Инициализируем БД при первом использовании
    init_db()

    # Создаем новую заметку
    note = Note(
        0,  # ID будет присвоен базой данных
        args.title,
        args.body,
        args.status,
        args.priority
    )

    # Сохраняем в БД
    save_note(note)

    # Выводим информацию о добавленной заметке
    print(f"✅ Заметка добавлена! ID: {note.id}")
    print(f"   Заголовок: {note.title}")
    print(f"   Статус: {note.status}, Приоритет: {note.priority}")
    print(f"   Создано: {note.created}")


def list_notes(args):
    """
    Показывает список заметок с возможностью фильтрации.

    Args:
        args: Объект аргументов с полями:
            - status (str, optional): Фильтр по статусу
            - priority (str, optional): Фильтр по приоритету

    Prints:
        Отформатированную таблицу с заметками или сообщение об отсутствии
    """
    init_db()

    notes = load_notes()
    filtered = notes.copy()  # Создаем копию для фильтрации

    # Фильтрация по статусу
    if args.status:
        filtered = [n for n in filtered if n.status == args.status]

    # Фильтрация по приоритету
    if args.priority:
        filtered = [n for n in filtered if n.priority == args.priority]

    if not filtered:
        print("📝 Заметки не найдены")
        return

    # Вывод таблицы с заметками
    print(f"📋 Всего заметок: {len(filtered)}")
    if args.status:
        print(f"   Фильтр по статусу: {args.status}")
    if args.priority:
        print(f"   Фильтр по приоритету: {args.priority}")

    print("-" * 100)
    # Заголовок таблицы
    print(f"{'ID':<4} | {'Заголовок':<30} | {'Статус':<12} | {'Приоритет':<9} | {'Создано':<19}")
    print("-" * 100)

    for note in filtered:
        # Обрезаем длинный заголовок
        title = note.title[:27] + "..." if len(note.title) > 30 else note.title
        print(f"{note.id:<4} | {title:<30} | {note.status:<12} | {note.priority:<9} | {note.created:<19}")

    print("-" * 100)


def search_notes_cli(args):
    """
    Ищет заметки по ключевому слову в заголовке или тексте.

    Args:
        args: Объект аргументов с полями:
            - keyword (str): Ключевое слово для поиска

    Prints:
        Список найденных заметок с фрагментами текста
    """
    init_db()
    found = search_notes(args.keyword)

    if not found:
        print(f"🔍 По запросу '{args.keyword}' ничего не найдено")
        return

    print(f"🔍 Найдено {len(found)} заметок по запросу '{args.keyword}':")
    print("-" * 100)

    for note in found:
        # Вывод основной информации
        print(f"ID: {note.id:3d} | {note.title:<30} | {note.status:10} | {note.priority:7}")

        # Поиск и выделение ключевого слова в тексте
        body_lower = note.body.lower()
        keyword_pos = body_lower.find(args.keyword.lower())

        if keyword_pos != -1:
            # Показываем фрагмент текста с ключевым словом
            start = max(0, keyword_pos - 30)
            end = min(len(note.body), keyword_pos + len(args.keyword) + 70)
            snippet = note.body[start:end]

            # Заменяем ключевое слово на выделенную версию
            original_word = note.body[keyword_pos:keyword_pos + len(args.keyword)]
            highlighted = snippet.replace(original_word, f"\033[1;33m{original_word}\033[0m")

            print(f"   ...{highlighted}..." if start > 0 else f"   {highlighted}")
        else:
            # Если ключевое слово только в заголовке, показываем начало текста
            print(f"   {note.body[:100]}{'...' if len(note.body) > 100 else ''}")

        print("-" * 100)


def delete_note_cli(args):
    """
    Удаляет заметку по указанному ID.

    Args:
        args: Объект аргументов с полями:
            - id (int): ID заметки для удаления

    Prints:
        Сообщение об успешном удалении или ошибке если заметка не найдена
    """
    init_db()
    # Проверяем существование заметки
    note = get_note_by_id(args.id)
    if not note:
        print(f"❌ Заметка с ID {args.id} не найдена")
        # Показываем доступные ID для справки
        notes = load_notes()
        available_ids = [n.id for n in notes[:5]]  # Первые 5 ID
        if available_ids:
            print(f"   Доступные ID: {', '.join(map(str, available_ids))}...")
        return

    # Удаляем заметку
    delete_note_by_id(args.id)

    print(f"🗑️  Заметка удалена!")
    print(f"   ID: {note.id}")
    print(f"   Заголовок: {note.title}")
