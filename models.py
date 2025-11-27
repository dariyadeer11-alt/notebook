import datetime

class Note:
    def __init__(self, id, title, body, status="todo", priority="medium"):
        self.id = id
        self.title = title
        self.body = body
        self.status = status
        self.priority = priority
        self.created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "status": self.status,
            "priority": self.priority,
            "created": self.created
        }

    @staticmethod
    def from_dict(data):
        note = Note(
            data["id"],
            data["title"],
            data["body"],
            data.get("status", "todo"),
            data.get("priority", "medium")
        )
        note.created = data.get("created", note.created)
        return note