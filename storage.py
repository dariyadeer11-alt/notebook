# notebookk/storage.py
import json
import os
from .models import Note

FILE_PATH = "notes.json"

def load_notes():
    if not os.path.exists(FILE_PATH):
        return []
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f) #загружает JSON в список словарей
            return [Note.from_dict(item) for item in data] #преобразует каждый словарь в список объектов
    except Exception:
        return []

def save_notes(notes):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump([n.to_dict() for n in notes], f, indent=4, ensure_ascii=False)