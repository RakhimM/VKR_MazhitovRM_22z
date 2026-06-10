import tkinter as tk
from tkinter import ttk, messagebox
from core.cell_db import CellDB
from ui.edit_cell_dialog import EditCellDialog


class CellDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.title("Типы ячеек")
        self.geometry("600x500")
        self.resizable(True, True)
        self.grab_set()

        self.db = CellDB()
        self.result = None

        self._create_widgets()
        self.changed = False
        self._load_cells()

        self.center_window()
        
        self.tree.bind(
            "<Double-1>",
            self.edit_selected
        )

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Название ячейки:").pack(
            anchor=tk.W,
            pady=5
        )

        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.pack(fill=tk.X, pady=5)

        ttk.Label(
            main_frame,
            text="Описание (необязательно):"
        ).pack(anchor=tk.W, pady=5)

        self.desc_entry = ttk.Entry(main_frame, width=50)
        self.desc_entry.pack(fill=tk.X, pady=5)

        columns = ("id", "name", "description")

        self.tree = ttk.Treeview(
            main_frame,
            columns=columns,
            show="headings",
            height=10
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название")
        self.tree.heading("description", text="Описание")

        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("name", width=180)
        self.tree.column("description", width=300)

        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            btn_frame,
            text="Сохранить",
            command=self._save
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            btn_frame,
            text="Удалить",
            command=self.delete_selected
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Отмена",
            command=self.destroy
        ).pack(side=tk.RIGHT)

    def _load_cells(self):
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        
        cells = self.db.get_all_cells()

        for cell in cells:
            self.tree.insert("", tk.END, values=cell)

    def _save(self):
        name = self.name_entry.get().strip()
        

        if not name:
            messagebox.showerror(
                "Ошибка",
                "Название ячейки не может быть пустым"
            )
            return

        desc = self.desc_entry.get().strip()

        try:
            new_id = self.db.add_cell(name, desc)

            self.result = (new_id, name)

            
            self._load_cells()

            
            self.name_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)

            messagebox.showinfo(
                "Успех",
                "Ячейка добавлена"
            )

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_selected(self):

        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Удаление",
                "Выберите ячейку"
            )
            return

        item = self.tree.item(selected[0])

        cell_id = item["values"][0]
        cell_name = item["values"][1]

        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить ячейку '{cell_name}'?"
        )

        if not confirm:
            return

        try:
            self.db.delete_cell(cell_id)

            
            self.tree.delete(selected[0])

            self.changed = True

            
            self.parent._load_cell_list()

            messagebox.showinfo(
                "Успех",
                "Ячейка удалена"
            )

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            
            
    def edit_selected(self, event=None):
        
        selected = self.tree.selection()

        if not selected:
            return

        item = self.tree.item(selected[0])

        values = item["values"]

        cell_id = values[0]
        name = values[1]
        description = values[2]

        dlg = EditCellDialog(
            self,
            cell_id,
            name,
            description
        )

        self.wait_window(dlg)

    def center_window(self):
        self.update_idletasks()

        w = self.winfo_width()
        h = self.winfo_height()

        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")