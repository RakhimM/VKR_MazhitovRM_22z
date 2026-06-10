import sqlite3
from core.db import Database


class CommandsDB:
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

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitor_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                command TEXT NOT NULL,
                is_ctrl INTEGER DEFAULT 0
            )
        """)

        self.conn.commit()

    def get_all_commands(self):

        self.cursor.execute("""
            SELECT
                id,
                name,
                description,
                command,
                is_ctrl
            FROM monitor_commands
            ORDER BY name
        """)

        return self.cursor.fetchall()

    def get_command(self, cmd_id):

        self.cursor.execute("""
            SELECT
                id,
                name,
                description,
                command,
                is_ctrl
            FROM monitor_commands
            WHERE id = ?
        """, (cmd_id,))

        return self.cursor.fetchone()

    def add_command(
        self,
        name,
        description,
        command,
        is_ctrl=False
    ):

        try:

            self.cursor.execute("""
                INSERT INTO monitor_commands
                (
                    name,
                    description,
                    command,
                    is_ctrl
                )
                VALUES (?, ?, ?, ?)
            """, (
                name,
                description,
                command,
                int(is_ctrl)
            ))

            self.conn.commit()

            return self.cursor.lastrowid

        except sqlite3.IntegrityError:

            raise ValueError(
                f"Команда '{name}' уже существует"
            )

    def update_command(
        self,
        cmd_id,
        name,
        description,
        command,
        is_ctrl=False
    ):

        try:

            self.cursor.execute("""
                UPDATE monitor_commands
                SET
                    name = ?,
                    description = ?,
                    command = ?,
                    is_ctrl = ?
                WHERE id = ?
            """, (
                name,
                description,
                command,
                int(is_ctrl),
                cmd_id
            ))

            self.conn.commit()

            if self.cursor.rowcount == 0:

                raise ValueError(
                    "Команда не найдена"
                )

        except sqlite3.IntegrityError:

            raise ValueError(
                f"Команда '{name}' уже существует"
            )

    def delete_command(self, cmd_id):

        self.cursor.execute("""
            DELETE FROM monitor_commands
            WHERE id = ?
        """, (cmd_id,))

        self.conn.commit()

        if self.cursor.rowcount == 0:

            raise ValueError(
                f"Команда с id={cmd_id} не найдена"
            )

    def get_command_by_name(self, name):

        self.cursor.execute("""
            SELECT
                id,
                name,
                description,
                command,
                is_ctrl
            FROM monitor_commands
            WHERE name = ?
        """, (name,))

        return self.cursor.fetchone()

    def command_exists(self, name):

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM monitor_commands
            WHERE name = ?
        """, (name,))

        return self.cursor.fetchone()[0] > 0

    def clear_all(self):

        self.cursor.execute("""
            DELETE FROM monitor_commands
        """)

        self.conn.commit()

    def close(self):

        if self.conn:
            self.conn.close()