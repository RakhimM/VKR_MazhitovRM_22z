import tkinter as tk
from tkinter import ttk, messagebox

from core.commands_db import CommandsDB


class CommandsDialog(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent

        self.title("Команды монитора")
        self.geometry("900x850")
        self.resizable(True, True)
        

        self.db = CommandsDB()

        self.selected_id = None
        self.form_visible = False

        self.create_widgets()
        self.load_commands()

        self.grab_set()
        
        self.tree.bind("<Delete>", self.on_delete_key)
        self.tree.bind("<Return>", self.on_enter_key)
        self.tree.bind("<Insert>", self.on_insert_key)

    def create_widgets(self):
        table_frame = ttk.Frame(self)

        table_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        columns = (
            "id",
            "name",
            "command",
            "ctrl",
            "description"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название")
        self.tree.heading("command", text="Команда")
        self.tree.heading("ctrl", text="Ctrl")
        self.tree.heading("description", text="Описание")

        self.tree.column("id", width=50)
        self.tree.column("name", width=150)
        self.tree.column("command", width=150)
        self.tree.column("ctrl", width=70)
        self.tree.column("description", width=400)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_select
        )
        
        self.tree.bind(
    "<Double-1>",
    self.on_enter_key
)

        self.toggle_btn = ttk.Button(
            self,
            text="▶ Параметры команды",
            command=self.toggle_form
        )

        self.toggle_btn.pack(
            fill=tk.X,
            padx=10,
            pady=(0, 5)
        )

        self.form = ttk.LabelFrame(
            self,
            text="Параметры команды"
        )

        ttk.Label(
            self.form,
            text="Название:"
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.name_var = tk.StringVar()

        ttk.Entry(
            self.form,
            textvariable=self.name_var,
            width=40
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
            sticky="ew"
        )

        ttk.Label(
            self.form,
            text="Команда:"
        ).grid(
            row=1,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.command_var = tk.StringVar()

        ttk.Entry(
            self.form,
            textvariable=self.command_var,
            width=40
        ).grid(
            row=1,
            column=1,
            padx=5,
            pady=5,
            sticky="ew"
        )

        self.ctrl_var = tk.BooleanVar()

        ttk.Checkbutton(
            self.form,
            text="Ctrl-команда",
            variable=self.ctrl_var
        ).grid(
            row=2,
            column=1,
            padx=5,
            pady=5,
            sticky="w"
        )

        ttk.Label(
            self.form,
            text="Описание:"
        ).grid(
            row=3,
            column=0,
            padx=5,
            pady=5,
            sticky="nw"
        )

        self.desc_text = tk.Text(
            self.form,
            height=4
        )

        self.desc_text.grid(
            row=3,
            column=1,
            padx=5,
            pady=5,
            sticky="ew"
        )

        self.form.columnconfigure(
            1,
            weight=1
        )

        btn_frame = ttk.Frame(self)

        btn_frame.pack(
            fill=tk.X,
            padx=10,
            pady=10
        )

        self.btn_new = ttk.Button(
            btn_frame,
            text="Новая команда",
            command=self.new_command
        )

        self.btn_new.pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            btn_frame,
            text="Добавить",
            command=self.add_command
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            btn_frame,
            text="Изменить",
            command=self.update_command
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            btn_frame,
            text="Удалить",
            command=self.delete_command
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            btn_frame,
            text="Очистить",
            command=self.clear_form
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            btn_frame,
            text="Закрыть",
            command=self.destroy
        ).pack(
            side=tk.RIGHT,
            padx=5
        )

    def toggle_form(self):
    
        if self.form_visible:

            self.form.pack_forget()

            self.toggle_btn.config(
                text="▶ Параметры команды"
            )

            
            self.btn_new.pack(
                side=tk.LEFT,
                padx=5
            )

            self.form_visible = False

        else:

            self.form.pack(
                fill=tk.X,
                padx=10,
                pady=5
            )

            self.toggle_btn.config(
                text="▼ Параметры команды"
            )

            
            self.btn_new.pack_forget()

            self.form_visible = True

    def load_commands(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self.db.get_all_commands():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    row[1],
                    row[3],
                    "Да" if row[4] else "Нет",
                    row[2]
                )
            )

    def on_select(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(
            selected[0]
        )["values"]

        self.selected_id = values[0]

        self.name_var.set(values[1])
        self.command_var.set(values[2])
        self.ctrl_var.set(values[3] == "Да")

        self.desc_text.delete(
            "1.0",
            tk.END
        )

        self.desc_text.insert(
            "1.0",
            values[4]
        )

        if not self.form_visible:
            self.toggle_form()

    def new_command(self):

        self.clear_form()

        if not self.form_visible:
            self.toggle_form()

    def add_command(self):
    
        try:

            self.db.add_command(
                self.name_var.get().strip(),
                self.desc_text.get("1.0", tk.END).strip(),
                self.command_var.get().strip(),
                self.ctrl_var.get()
            )

            self.load_commands()
            self.clear_form()

            if self.form_visible:
                self.toggle_form()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_command(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "Внимание",
                "Выберите команду"
            )

            return

        try:

            self.db.update_command(
    self.selected_id,
    self.name_var.get().strip(),
    self.desc_text.get("1.0", tk.END).strip(),
    self.command_var.get().strip(),
    self.ctrl_var.get()
)

            self.load_commands()

        except Exception as e:

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

    def delete_command(self):

        if self.selected_id is None:
            return

        if not messagebox.askyesno(
            "Удаление",
            "Удалить выбранную команду?"
        ):
            return

        try:

            self.db.delete_command(
    self.selected_id
)

            self.load_commands()
            self.clear_form()

        except Exception as e:

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

    def clear_form(self):

        self.selected_id = None

        self.name_var.set("")
        self.command_var.set("")
        self.ctrl_var.set(False)

        self.desc_text.delete(
            "1.0",
            tk.END
        )

    def on_delete_key(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        self.delete_command()
        
    def on_enter_key(self, event=None):
    
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0])["values"]

        command = values[2]          
        is_ctrl = values[3] == "Да" 

        self.parent.send_saved_command(
            command,
            is_ctrl
        )
        
    def on_insert_key(self, event=None):
        self.new_command()