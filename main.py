"""
Основной модуль приложения notebookk.

Обрабатывает аргументы командной строки и запускает:
- CLI интерфейс с командами (add, list, search, delete)
- GUI интерфейс (tkinter)
Или автоматически определяет режим работы.
"""

import argparse
import sys
import tkinter as tk
from .gui import NoteApp
from .commands import add_note, list_notes, search_notes_cli as search_notes, delete_note_cli as delete_note

def setup_cli_parser():
    """
    Настраивает парсер аргументов командной строки для CLI интерфейса.

    Returns:
        argparse.ArgumentParser: Настроенный парсер с подкомандами:
            - add: Добавить новую заметку
            - list: Показать список заметок
            - search: Поиск заметок по ключевому слову
            - delete: Удалить заметку по ID
    """
    parser = argparse.ArgumentParser(
        prog="notebookk",
        description="📝 Менеджер заметок с CLI и GUI интерфейсами",
        epilog="Примеры:\n"
               "  python -m notebookk add --title 'Заголовок' --body 'Текст'\n"
               "  python -m notebookk list --status todo\n"
               "  python -m notebookk search --keyword 'важно'\n"
               "  python -m notebookk delete --id 1\n"
               "  python -m notebookk --gui  # Запуск графического интерфейса"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="Доступные команды",
        description="Используйте 'notebookk <команда> --help' для справки по конкретной команде"
    )

    # Команда add
    add_parser = subparsers.add_parser(
        'add',
        help='Добавить новую заметку',
        description='Создание новой заметки с указанными параметрами'
    )
    add_parser.add_argument('--title', required=True, help='Заголовок заметки')
    add_parser.add_argument('--body', required=True, help='Текст заметки')
    add_parser.add_argument(
        '--status',
        default='todo',
        choices=['todo', 'in_progress', 'done'],
        help='Статус заметки (default: todo)'
    )
    add_parser.add_argument(
        '--priority',
        default='medium',
        choices=['low', 'medium', 'high'],
        help='Приоритет заметки (default: medium)'
    )
    add_parser.set_defaults(func=add_note)

    # Команда list
    list_parser = subparsers.add_parser(
        'list',
        help='Показать список заметок',
        description='Отображение списка заметок с возможностью фильтрации'
    )
    list_parser.add_argument(
        '--status',
        choices=['todo', 'in_progress', 'done'],
        help='Фильтр по статусу'
    )
    list_parser.add_argument(
        '--priority',
        choices=['low', 'medium', 'high'],
        help='Фильтр по приоритету'
    )
    list_parser.set_defaults(func=list_notes)

    # Команда search
    search_parser = subparsers.add_parser(
        'search',
        help='Поиск заметок',
        description='Поиск заметок по ключевому слову в заголовке или тексте'
    )
    search_parser.add_argument('--keyword', required=True, help='Ключевое слово для поиска')
    search_parser.set_defaults(func=search_notes)

    # Команда delete
    delete_parser = subparsers.add_parser(
        'delete',
        help='Удалить заметку',
        description='Удаление заметки по её ID'
    )
    delete_parser.add_argument('--id', required=True, type=int, help='ID заметки для удаления')
    delete_parser.set_defaults(func=delete_note)

    # Общий аргумент для GUI
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Запустить графический интерфейс (вместо CLI)'
    )

    return parser


def main():
    """
    Основная функция приложения.

    Определяет режим работы:
    1. Если есть аргументы командной строки -> CLI режим
    2. Если указан --gui или нет аргументов -> GUI режим
    3. Выводит справку если команда не распознана
    """
    parser = setup_cli_parser()

    # Если запущено напрямую или есть аргументы
    if __name__ == "__main__" or len(sys.argv) > 1:
        try:
            args = parser.parse_args()
        except SystemExit:
            return  # Выход при ошибке парсинга (например, --help)

        if args.gui:
            # Запуск графического интерфейса
            root = tk.Tk()
            app = NoteApp(root)
            root.mainloop()
        elif hasattr(args, 'func'):
            # Выполнение CLI команды
            args.func(args)
        else:
            # Вывод справки если команда не указана
            parser.print_help()
    else:
        # Автоматический запуск GUI если нет аргументов
        root = tk.Tk()
        app = NoteApp(root)
        root.mainloop()


if __name__ == "__main__":
    main()