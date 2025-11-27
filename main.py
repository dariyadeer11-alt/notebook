import argparse
import sys
import tkinter as tk
from .gui import NoteApp
from .commands import add_note, list_notes, search_notes, delete_note


def setup_cli_parser():
    """Настройка парсера для CLI-команд"""
    parser = argparse.ArgumentParser(description="Менеджер заметок")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Команда add
    add_parser = subparsers.add_parser('add', help='Добавить новую заметку')
    add_parser.add_argument('--title', required=True, help='Заголовок заметки')
    add_parser.add_argument('--body', required=True, help='Текст заметки')
    add_parser.add_argument('--status', default='todo', help='Статус (todo, in_progress, done)')
    add_parser.add_argument('--priority', default='medium', help='Приоритет (low, medium, high)')
    add_parser.set_defaults(func=add_note)

    # Команда list
    list_parser = subparsers.add_parser('list', help='Показать список заметок')
    list_parser.add_argument('--status', help='Фильтр по статусу')
    list_parser.add_argument('--priority', help='Фильтр по приоритету')
    list_parser.set_defaults(func=list_notes)

    # Команда search
    search_parser = subparsers.add_parser('search', help='Поиск заметок')
    search_parser.add_argument('--keyword', required=True, help='Ключевое слово для поиска')
    search_parser.set_defaults(func=search_notes)

    # Команда delete
    delete_parser = subparsers.add_parser('delete', help='Удалить заметку')
    delete_parser.add_argument('--id', required=True, type=int, help='ID заметки для удаления')
    delete_parser.set_defaults(func=delete_note)

    return parser


def main():
    # Сначала проверяем, запущен ли как модуль
    if __name__ == "__main__" or len(sys.argv) > 1:
        parser = setup_cli_parser()
        parser.add_argument('--gui', action='store_true', help='Запустить графический интерфейс')

        try:
            args = parser.parse_args()
        except SystemExit:
            return

        if args.gui:
            root = tk.Tk()
            app = NoteApp(root)
            root.mainloop()
        elif hasattr(args, 'func'):
            # CLI-команда
            args.func(args)
        else:
            parser.print_help()
    else:
        # Если запускается как модуль без аргументов — открываем GUI
        root = tk.Tk()
        app = NoteApp(root)
        root.mainloop()


if __name__ == "__main__":
    main()