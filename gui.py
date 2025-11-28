# notebookk/gui.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from .storage import load_notes, save_notes
from .models import Note

class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер заметок")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f4f4f4")

        self.notes = load_notes()
        self.next_id = max([n.id for n in self.notes], default=0) + 1

        self.build_ui()
        self.refresh_list()

    def build_ui(self):
        # === Левая панель: добавление заметки ===
        left = tk.Frame(self.root, bg="#f4f4f4")
        left.pack(side=tk.LEFT, padx=25, pady=25, fill=tk.Y)
        #заголовок
        tk.Label(left, text="Новая заметка", font=("Segoe UI", 16, "bold"), bg="#f4f4f4").pack(pady=(0, 15))

        tk.Label(left, text="Заголовок", bg="#f4f4f4", font=("Segoe UI", 10)).pack(anchor="w")
        #поле ввода
        self.title_entry = tk.Entry(left, width=40, font=("Segoe UI", 10))
        self.title_entry.pack(pady=(0, 10))

        tk.Label(left, text="Текст заметки", bg="#f4f4f4", font=("Segoe UI", 10)).pack(anchor="w")
        #текстовое поле с прокруткой
        self.body_text = scrolledtext.ScrolledText(left, width=40, height=10, font=("Segoe UI", 10))
        self.body_text.pack(pady=(0, 20))

        tk.Label(left, text="Статус", bg="#f4f4f4").pack(anchor="w")

        self.status_var = tk.StringVar(value="todo")
        #выпадающий список
        ttk.Combobox(left, textvariable=self.status_var,
                     values=["todo", "in_progress", "done"], state="readonly", width=37).pack(pady=(0, 10))

        tk.Label(left, text="Приоритет", bg="#f4f4f4").pack(anchor="w")
        self.priority_var = tk.StringVar(value="medium")
        ttk.Combobox(left, textvariable=self.priority_var,
                     values=["low", "medium", "high"], state="readonly", width=37).pack(pady=(0, 25))

        tk.Button(left, text="Добавить заметку", bg="#2196F3", fg="white",
                  font=("Segoe UI", 11, "bold"), height=2, command=self.add_note).pack()

        # === Правая панель: список, поиск, фильтры ===
        right = tk.Frame(self.root, bg="#f4f4f4")
        right.pack(side=tk.RIGHT, padx=25, pady=25, fill=tk.BOTH, expand=True)

        # Поиск
        search_frame = tk.Frame(right, bg="#f4f4f4")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(search_frame, text="Поиск:", bg="#f4f4f4").pack(side=tk.LEFT)
        self.search_var = tk.StringVar() #переменная для поиска, следит за изменениями
        tk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        tk.Button(search_frame, text="Найти", command=self.refresh_list).pack(side=tk.RIGHT)

        # Фильтры
        filter_frame = tk.Frame(right, bg="#f4f4f4")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(filter_frame, text="Статус:", bg="#f4f4f4").pack(side=tk.LEFT)
        self.filter_status = tk.StringVar()
        ttk.Combobox(filter_frame, textvariable=self.filter_status, values=["", "todo", "in_progress", "done"], width=15).pack(side=tk.LEFT, padx=5)
        tk.Label(filter_frame, text="Приоритет:", bg="#f4f4f4").pack(side=tk.LEFT, padx=(20,0))
        self.filter_priority = tk.StringVar()
        ttk.Combobox(filter_frame, textvariable=self.filter_priority, values=["", "low", "medium", "high"], width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(filter_frame, text="Фильтр", command=self.refresh_list).pack(side=tk.LEFT, padx=10)

        # Таблица заметок
        columns = ("id", "title", "status", "priority", "created")
        self.tree = ttk.Treeview(right, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100 if col != "title" else 300, anchor="w" if col == "title" else "center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.show_full_note) #по двойному клику разворачиваем заметку

        btn_frame = tk.Frame(right, bg="#f4f4f4")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Удалить выбранную", bg="#f44336", fg="white", command=self.delete_note).pack()

    def add_note(self):
        title = self.title_entry.get().strip()
        body = self.body_text.get(1.0, tk.END).strip()
        if not title or not body:
            messagebox.showwarning("Ошибка", "Введите заголовок и текст заметки!")
            return

        note = Note(self.next_id, title, body, self.status_var.get(), self.priority_var.get())
        self.notes.append(note)
        self.next_id += 1
        save_notes(self.notes)

        self.title_entry.delete(0, tk.END) #очищаем
        self.body_text.delete(1.0, tk.END)
        self.refresh_list() #добавляем в список
        messagebox.showinfo("Успех", f"Заметка добавлена! ID: {note.id}")

    def refresh_list(self):
        for i in self.tree.get_children(): #по элементам таблицы
            self.tree.delete(i)

        search = self.search_var.get().lower() #получаем поисковой запрос
        f_status = self.filter_status.get()
        f_priority = self.filter_priority.get()

        for note in self.notes:
            if search and search not in note.title.lower() and search not in note.body.lower():
                continue
            if f_status and note.status != f_status:
                continue
            if f_priority and note.priority != f_priority:
                continue
            self.tree.insert("", tk.END, values=(note.id, note.title, note.status, note.priority, note.created)) #само добавление

    def show_full_note(self, event):
        sel = self.tree.selection() #выбранная строка
        if not sel: return
        item = self.tree.item(sel[0]) #сами данные строки
        note_id = item["values"][0] #получаем id
        note = next(n for n in self.notes if n.id == note_id) #находим заметку по id

        win = tk.Toplevel(self.root)
        win.title(f"Заметка #{note.id} — {note.title}")
        win.geometry("600x500")

        tk.Label(win, text=note.title, font=("Segoe UI", 16, "bold")).pack(pady=10)
        tk.Label(win, text=f"Создано: {note.created} | Статус: {note.status} | Приоритет: {note.priority}").pack()
        #текстовое прокручивающееся поле, добавляем текст, оставляем для чтения, указываем размещение
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, padx=15, pady=15, font=("Segoe UI", 10))
        text.insert(tk.END, note.body)
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def delete_note(self):
        sel = self.tree.selection() #получаем строку
        if not sel:
            messagebox.showwarning("Ошибка", "Выберите заметку для удаления")
            return
        if messagebox.askyesno("Удалить", "Точно удалить эту заметку?"):
            #получаем данные, фильтруем, сохраняем изменения
            item = self.tree.item(sel[0])
            note_id = item["values"][0]
            self.notes = [n for n in self.notes if n.id != note_id]
            save_notes(self.notes)
            self.refresh_list()
