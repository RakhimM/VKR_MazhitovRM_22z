import sqlite3
from core.db import Database
class CellDB:
    _instance = None
    _db_path = "app.db"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        
        db = Database()

        self.conn = db.conn
        self.cursor = db.cursor

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cell_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        ''')

        self.conn.commit()

        self.cursor.execute("SELECT COUNT(*) FROM cell_types")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                "INSERT INTO cell_types (name, description) VALUES (?, ?)",
                ("Стандартная", "Разрабатываемая ячейка")
            )
            self.conn.commit()

    def get_all_cells(self):
        self.cursor.execute(
            "SELECT id, name, description FROM cell_types ORDER BY name"
        )
        return self.cursor.fetchall()

    def add_cell(self, name, description):
        try:
            self.cursor.execute(
                "INSERT INTO cell_types (name, description) VALUES (?, ?)",
                (name, description)
            )
            self.conn.commit()
            return self.cursor.lastrowid

        except sqlite3.IntegrityError:
            raise ValueError(f"Ячейка с именем '{name}' уже существует")
        
        
    def update_cell(self, cell_id, name, description):
        try:
            self.cursor.execute(
                """
                UPDATE cell_types
                SET name = ?, description = ?
                WHERE id = ?
                """,
                (name, description, cell_id)
            )

            self.conn.commit()

            if self.cursor.rowcount == 0:
                raise ValueError("Ячейка не найдена")

        except sqlite3.IntegrityError:
            raise ValueError(
                f"Ячейка с именем '{name}' уже существует"
            )

    def delete_cell(self, cell_id):
        """Удаляет ячейку по id."""
        self.cursor.execute(
            "DELETE FROM cell_types WHERE id = ?",
            (cell_id,)
        )

        self.conn.commit()

        if self.cursor.rowcount == 0:
            raise ValueError(f"Ячейка с id={cell_id} не найдена")

    def get_cell_name(self, cell_id):
        self.cursor.execute(
            "SELECT name FROM cell_types WHERE id = ?",
            (cell_id,)
        )

        row = self.cursor.fetchone()
        return row[0] if row else None

    def close(self):
        if self.conn:
            self.conn.close()