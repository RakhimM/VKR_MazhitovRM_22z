import sqlite3


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance.conn = sqlite3.connect(
                "app.db"
            )

            cls._instance.cursor = (
                cls._instance.conn.cursor()
            )

        return cls._instance