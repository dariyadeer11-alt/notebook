"""
Модуль графического интерфейса приложения.

Содержит класс NoteApp, реализующий GUI на основе tkinter.
Предоставляет полный функционал для управления заметками
через интуитивно понятный графический интерфейс.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from .storage import load_notes, save_note, delete_note_by_id, get_note_by_id
from .models import Note
from notebookk.database import init_db


class NoteApp:
    """
    Главный класс графического интерфейса приложения notebookk.

    Attributes:
        root (tk.Tk): Основное окно приложения
        notes (list[Note]): Список загруженных заметок
        next_id (int): Следующий ID для новой заметки
    """

    def __init__(self, root):
        """
        Инициализирует графический интерфейс.

        Args:
            root (tk.Tk): Корневое окно tkinter
        """
        self.root = root
        self.root.title("📒 Менеджер заметок Notebookk")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f4f4f4")

        # Инициализируем БД
        init_db()

        # Загружаем заметки и определяем следующий ID
        self.notes = load_notes()
        self.next_id = max([n.id for n in self.notes], default=0) + 1

        # Строим интерфейс
        self.build_ui()
        self.refresh_list()

        # Центрируем окно на экране
        self.center_window()

    def center_window(self):
        """Центрирует окно приложения на экране."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def build_ui(self):
        """
        Строит все элементы графического интерфейса.

        Интерфейс разделен на две основные части:
        1. Левая панель: Форма добавления новой заметки
        2. Правая панель: Список заметок с поиском и фильтрами
        """
        # === Левая панель: добавление заметки ===
        left = tk.Frame(self.root, bg="#f4f4f4")
        left.pack(side=tk.LEFT, padx=25, pady=25, fill=tk.Y)

        # Заголовок панели
        tk.Label(
            left,
            text="📝 Новая заметка",
            font=("Segoe UI", 16, "bold"),
            bg="#f4f4f4"
        ).pack(pady=(0, 15))

        # Поле для заголовка
        tk.Label(left, text="Заголовок", bg="#f4f4f4", font=("Segoe UI", 10)).pack(anchor="w")
        self.title_entry = tk.Entry(left, width=40, font=("Segoe UI", 10))
        self.title_entry.pack(pady=(0, 10))

        # Поле для текста заметки
        tk.Label(left, text="Текст заметки", bg="#f4f4f4", font=("Segoe UI", 10)).pack(anchor="w")
        self.body_text = scrolledtext.ScrolledText(
            left,
            width=40,
            height=10,
            font=("Segoe UI", 10)
        )
        self.body_text.pack(pady=(0, 20))

        # Выбор статуса
        tk.Label(left, text="Статус", bg="#f4f4f4", font=("Segoe UI", 10)).pack(anchor="w")
        self.status_var = tk.StringVar(value="todo")
        ttk.Combobox(
            left,
            textvariable=self.status_var,
            values=["todo", "in_progress", "done"],
            state="readonly",
            width=37,
            font=("Segoe UI", 10)
        ).pack(pady=(0, 10))

        # Выбор приоритета
        tk.Label(left, text="Приоритет", bg="#f4f4f4", font=("Segoe UI", 10)).pack(anchor="w")
        self.priority_var = tk.StringVar(value="medium")
        ttk.Combobox(
            left,
            textvariable=self.priority_var,
            values=["low", "medium", "high"],
            state="readonly",
            width=37,
            font=("Segoe UI", 10)
        ).pack(pady=(0, 25))

        # Кнопка добавления
        tk.Button(
            left,
            text="✅ Добавить заметку",
            bg="#2196F3",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            height=2,
            command=self.add_note,
            cursor="hand2"
        ).pack(fill=tk.X)

        # === Правая панель: список заметок ===
        right = tk.Frame(self.root, bg="#f4f4f4")
        right.pack(side=tk.RIGHT, padx=25, pady=25, fill=tk.BOTH, expand=True)

        # Поиск
        search_frame = tk.Frame(right, bg="#f4f4f4")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(search_frame, text="🔍 Поиск:", bg="#f4f4f4", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        # Привязываем событие изменения текста для автоматического поиска
        self.search_var.trace("w", lambda *args: self.refresh_list())
        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=40,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # Фильтры
        filter_frame = tk.Frame(right, bg="#f4f4f4")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filter_frame, text="📊 Статус:", bg="#f4f4f4", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.filter_status = tk.StringVar()
        self.filter_status.trace("w", lambda *args: self.refresh_list())
        ttk.Combobox(
            filter_frame,
            textvariable=self.filter_status,
            values=["Все", "todo", "in_progress", "done"],
            width=15,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)
        self.filter_status.set("Все")

        tk.Label(filter_frame, text="🎯 Приоритет:", bg="#f4f4f4", font=("Segoe UI", 10)).pack(side=tk.LEFT,
                                                                                              padx=(20, 0))
        self.filter_priority = tk.StringVar()
        self.filter_priority.trace("w", lambda *args: self.refresh_list())
        ttk.Combobox(
            filter_frame,
            textvariable=self.filter_priority,
            values=["Все", "low", "medium", "high"],
            width=15,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)
        self.filter_priority.set("Все")

        # Таблица заметок
        columns = ("id", "title", "status", "priority", "created")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", height=15)

        # Настраиваем заголовки колонок
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Заголовок")
        self.tree.heading("status", text="Статус")
        self.tree.heading("priority", text="Приоритет")
        self.tree.heading("created", text="Создано")

        # Настраиваем ширину колонок
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("title", width=300, anchor="w")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("priority", width=100, anchor="center")
        self.tree.column("created", width=150, anchor="center")

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Привязываем двойной клик для просмотра заметки
        self.tree.bind("<Double-1>", self.show_full_note)

        # Панель кнопок
        btn_frame = tk.Frame(right, bg="#f4f4f4")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="🗑️ Удалить выбранную",
            bg="#f44336",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.delete_note,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🔄 Обновить список",
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.refresh_list,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

    def add_note(self):
        """
        Добавляет новую заметку из данных формы.
        """
        title = self.title_entry.get().strip()
        body = self.body_text.get(1.0, tk.END).strip()

        # Валидация данных (без изменений)
        if not title:
            messagebox.showwarning("Ошибка", "Введите заголовок заметки!")
            self.title_entry.focus()
            return
        if not body:
            messagebox.showwarning("Ошибка", "Введите текст заметки!")
            self.body_text.focus()
            return
        if len(title) > 100:
            messagebox.showwarning("Ошибка", "Заголовок слишком длинный (макс. 100 символов)")
            return

        # Создаем новую заметку
        note = Note(
            self.next_id,  # Временный ID, будет переопределен БД
            title,
            body,
            self.status_var.get(),
            self.priority_var.get()
        )

        # Сохраняем в БД
        try:
            save_notes(note)  # Этот метод обновит ID и created
            self.next_id = max(self.next_id, note.id + 1)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить заметку: {e}")
            return

        # Обновляем локальный список
        self.notes = load_notes()

        # Очищаем форму
        self.title_entry.delete(0, tk.END)
        self.body_text.delete(1.0, tk.END)

        # Обновляем список и показываем сообщение
        self.refresh_list()
        messagebox.showinfo(
            "Успех",
            f"✅ Заметка добавлена!\n\n"
            f"ID: {note.id}\n"
            f"Заголовок: {title[:50]}{'...' if len(title) > 50 else ''}"
        )


    def refresh_list(self, event=None):
        """
        Обновляет список заметок с учетом фильтров и поиска.

        Args:
            event: Событие tkinter (опционально)
        """
        # Очищаем текущий список
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получаем текущие значения фильтров
        search = self.search_var.get().lower()
        f_status = self.filter_status.get()
        f_priority = self.filter_priority.get()

        # Преобразуем "Все" в пустую строку для фильтрации
        if f_status == "Все":
            f_status = ""
        if f_priority == "Все":
            f_priority = ""

        # Добавляем отфильтрованные заметки
        for note in self.notes:
            # Фильтрация по поиску
            if search and search not in note.title.lower() and search not in note.body.lower():
                continue
            # Фильтрация по статусу
            if f_status and note.status != f_status:
                continue
            # Фильтрация по приоритету
            if f_priority and note.priority != f_priority:
                continue

            # Добавляем заметку в таблицу
            self.tree.insert(
                "",
                tk.END,
                values=(note.id, note.title, note.status, note.priority, note.created)
            )

    def show_full_note(self, event):
        """
        Показывает полное содержимое выбранной заметки в отдельном окне.

        Args:
            event: Событие двойного клика
        """
        # Получаем выбранную заметку
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        note_id = item["values"][0]

        # Находим заметку по ID
        try:
            note = next(n for n in self.notes if n.id == note_id)
        except StopIteration:
            messagebox.showerror("Ошибка", "Заметка не найдена!")
            return

        # Создаем окно просмотра
        win = tk.Toplevel(self.root)
        win.title(f"📄 Заметка #{note.id} — {note.title}")
        win.geometry("600x500")
        win.configure(bg="#f4f4f4")

        # Центрируем окно просмотра
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        win.geometry(f'{width}x{height}+{x}+{y}')

        # Заголовок заметки
        title_label = tk.Label(
            win,
            text=note.title,
            font=("Segoe UI", 16, "bold"),
            bg="#f4f4f4",
            wraplength=550
        )
        title_label.pack(pady=10)

        # Метаданные заметки
        meta_frame = tk.Frame(win, bg="#f4f4f4")
        meta_frame.pack(pady=(0, 10))

        tk.Label(
            meta_frame,
            text=f"🆔 ID: {note.id}",
            bg="#f4f4f4",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            meta_frame,
            text=f"📅 Создано: {note.created}",
            bg="#f4f4f4",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            meta_frame,
            text=f"📊 Статус: {note.status}",
            bg="#f4f4f4",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            meta_frame,
            text=f"🎯 Приоритет: {note.priority}",
            bg="#f4f4f4",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)

        # Текст заметки с прокруткой
        text_frame = tk.Frame(win)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            padx=15,
            pady=15,
            bg="#ffffff",
            relief=tk.FLAT,
            borderwidth=1
        )
        text_area.pack(fill=tk.BOTH, expand=True)

        # Вставляем текст и делаем доступным для копирования
        text_area.insert(tk.END, note.body)
        text_area.configure(state=tk.DISABLED)  # Только для чтения

        # Добавляем кнопку копирования
        btn_frame = tk.Frame(win, bg="#f4f4f4")
        btn_frame.pack(pady=(0, 10))

        tk.Button(
            btn_frame,
            text="📋 Копировать текст",
            command=lambda: self.copy_to_clipboard(note.body),
            cursor="hand2",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)

    def copy_to_clipboard(self, text):
        """Копирует текст в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Успех", "Текст скопирован в буфер обмена!")

    def delete_note(self):
        """Удаляет выбранную заметку с подтверждением."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите заметку для удаления")
            return

        item = self.tree.item(selection[0])
        note_id = item["values"][0]

        # Находим заметку для показа информации
        note_to_delete = get_note_by_id(note_id)
        if not note_to_delete:
            messagebox.showerror("Ошибка", "Заметка не найдена!")
            return

        # Запрашиваем подтверждение (без изменений)
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить заметку?\n\n"
            f"ID: {note_to_delete.id}\n"
            f"Заголовок: {note_to_delete.title}\n"
            f"Статус: {note_to_delete.status}\n"
            f"Приоритет: {note_to_delete.priority}"
        )

        if not confirm:
            return

        # Удаляем заметку из БД
        try:
            delete_note_by_id(note_id)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить заметку: {e}")
            return

        # Обновляем локальный список
        self.notes = load_notes()

        # Обновляем список
        self.refresh_list()

        # Показываем сообщение об успехе
        messagebox.showinfo(
            "Успех",
            f"✅ Заметка удалена!\n\n"
            f"ID: {note_id}\n"
            f"Заголовок: {note_to_delete.title}"
        )