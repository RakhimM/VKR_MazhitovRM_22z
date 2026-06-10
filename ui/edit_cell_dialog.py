import tkinter as tk
from tkinter import ttk, messagebox

from core.cell_db import CellDB


class EditCellDialog(tk.Toplevel):

    def __init__(self, parent, cell_id, name, description):
        super().__init__(parent)

        self.parent = parent
        self.cell_id = cell_id

        self.db = CellDB()

        self.title("Редактирование ячейки")
        self.geometry("400x220")
        self.resizable(True, True)

        self.grab_set()

        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="Название").pack(anchor=tk.W)

        self.name_entry = ttk.Entry(main)
        self.name_entry.pack(fill=tk.X, pady=5)

        self.name_entry.insert(0, name)

        ttk.Label(main, text="Описание").pack(anchor=tk.W)

        self.desc_entry = tk.Text(
            main,
            height=1,
            wrap=tk.WORD
        )

        self.desc_entry.pack(
            fill=tk.BOTH,
            expand=True,
            pady=5
        )

        self.desc_entry.insert(
            "1.0",
            description or ""
        )

        btns = ttk.Frame(main)
        btns.pack(fill=tk.X, pady=15)

        ttk.Button(
            btns,
            text="Сохранить",
            command=self.save
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            btns,
            text="Отмена",
            command=self.destroy
        ).pack(side=tk.RIGHT)

    def save(self):

        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()

        if not name:
            messagebox.showerror(
                "Ошибка",
                "Название не может быть пустым"
            )
            return

        try:
            self.db.update_cell(
                self.cell_id,
                name,
                desc
            )

            self.parent._load_cells()

            self.parent.parent._load_cell_list()

            messagebox.showinfo(
                "Успех",
                "Ячейка обновлена"
            )

            self.destroy()

        except ValueError as e:
            messagebox.showerror(
                "Ошибка",
                str(e)
            )