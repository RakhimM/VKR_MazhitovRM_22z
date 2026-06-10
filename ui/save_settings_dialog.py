import tkinter as tk
from tkinter import ttk, filedialog

from config import config, save_config


class SaveSettingsDialog(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Настройки сохранения")
        self.geometry("500x200")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.auto_save_var = tk.BooleanVar(
            value=config.get("auto_save_log", False)
        )

        ttk.Checkbutton(
            self,
            text="Постоянно сохранять лог при закрытии",
            variable=self.auto_save_var
        ).pack(anchor=tk.W, padx=15, pady=15)

        path_frame = ttk.Frame(self)
        path_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Label(path_frame, text="Папка:").pack(side=tk.LEFT)

        self.path_var = tk.StringVar(
            value=config.get("log_save_dir", "")
        )

        ttk.Entry(
            path_frame,
            textvariable=self.path_var
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(
            path_frame,
            text="Выбрать",
            command=self.select_folder
        ).pack(side=tk.LEFT)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)

        ttk.Button(
            btn_frame,
            text="Сохранить",
            command=self.save
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            btn_frame,
            text="Отмена",
            command=self.destroy
        ).pack(side=tk.LEFT)

    def select_folder(self):

        folder = filedialog.askdirectory(
            parent=self,
            title="Выберите папку"
        )

        if folder:
            self.path_var.set(folder)

    def save(self):

        config["auto_save_log"] = self.auto_save_var.get()
        config["log_save_dir"] = self.path_var.get()

        save_config(config)

        self.destroy()