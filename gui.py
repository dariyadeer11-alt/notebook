# notebook/gui.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from .storage import load_notes, save_notes
from .models import Note

class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер заметок")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")
        self.notes = load_notes()
        self.next_id = max([n.id for n in self.notes], default=0) + 1

        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # === Левая часть — форма добавления ===
        left_frame = tk.Frame(self.root, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.Y)

        tk.Label(left_frame, text="Новая заметка", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=(0,10))


        tk.Label(left_frame, text="Приоритет:", bg="#f0f0f0").pack(anchor="w")
        self.priority_var = tk.StringVar(value="medium")
        ttk.Combobox(left_frame, textvariable=self.priority_var, values=["low", "medium", "high"], state="readonly", width=37).pack(pady=(0,20))

        tk.Button(left_frame, text="Добавить заметку", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.add_note).pack(pady=10)

        # === Правая часть — список и поиск ===
        right_frame = tk.Frame(self.root, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Поиск
        search_frame = tk.Frame(right_frame, bg="#f0f0f0")
        search_frame.pack(fill=tk.X, pady=(0,10))
        tk.Label(search_frame, text="Поиск:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,5))
        tk.Button(search_frame, text="Найти", command=self.refresh_list).pack(side=tk.RIGHT)

        # Фильтры
        filter_frame = tk.Frame(right_frame, bg="#f0f0f0")
        filter_frame.pack(fill=tk.X, pady=(0,10))
        tk.Label(filter_frame, text="Фильтр по статусу:").pack(side=tk.LEFT)
        self.filter_status = tk.StringVar()
        ttk.Combobox(filter_frame, textvariable=self.filter_status, values=["", "todo", "in_progress", "done"], width=15).pack(side=tk.LEFT, padx=5)
        tk.Label(filter_frame, text="Приоритет:").pack(side=tk.LEFT)
        self.filter_priority = tk.StringVar()
        ttk.Combobox(filter_frame, textvariable=self.filter_priority, values=["", "low", "medium", "high"], width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(filter_frame, text="Применить", command=self.refresh_list).pack(side=tk.LEFT, padx=5)

        # Список заметок
        columns = ("id", "title", "status", "priority", "created")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=120 if col != "title" else 250)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.show_full_note)
        tk.Button(right_frame, text="Удалить выбранную", bg="#f44336", fg="white", command=self.delete_note).pack(pady=5)

    def add_note(self):
        title = self.title_entry.get().strip()
        body = self.body_text.get(1.0, tk.END).strip()
        if not title or not body:
            messagebox.showwarning("Ошибка", "Заполните заголовок и текст!")
            return

        note = Note(self.next_id, title, body, self.status_var.get(), self.priority_var.get())
        self.notes.append(note)
        self.next_id += 1
        save_notes(self.notes)

    def show_full_note(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        note_id = item["values"][0]
        note = next(n for n in self.notes if n.id == note_id)

        win = tk.Toplevel(self.root)
        win.title(f"Заметка #{note.id}")
        win.geometry("500x400")

        tk.Label(win, text=note.title, font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(win, text=f"Создано: {note.created} | Статус: {note.status} | Приоритет: {note.priority}").pack()
