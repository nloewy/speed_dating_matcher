from werkzeug.security import generate_password_hash
from flask import current_app as app

class Group:

    def __init__(self, description, name, owner_id):
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self._owner=None

    @property
    def owner(self):
        if not self._owner:  
            rows = app.db.execute("""SELECT name FROM Users WHERE id = :id """, id=self.owner_id)
            self._owner = rows[0][0]
        return self._owner

    @staticmethod
    def create_group(name, description, password, owner):
        try:
            rows = app.db.execute("""
                INSERT INTO Groups(name, description, password, owner)
                VALUES(:name, :description, :password, :owner) RETURNING id
                """,
                name=name, description = description, password=generate_password_hash(password), owner=owner)
            return rows[0][0]
        except Exception as e:
            # likely name already in use
            print(f"Group Creation error: {str(e)}")
            return None

    @staticmethod
    def get_all():
        rows = app.db.execute("""
                SELECT name, description, owner FROM groups
                """)
        return [Group(*row) for row in rows] if rows else None
