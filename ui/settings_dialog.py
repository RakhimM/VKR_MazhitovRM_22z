import tkinter as tk
from tkinter import ttk, messagebox
from core.cell_db import CellDB

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = CellDB()

        self.title("Настройки приложения")
        self.geometry("500x550")
        self.resizable(False, False)
        self.grab_set()

        self._create_widgets()
        self._load_settings()
        self.center_window()

    def _create_widgets(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        row = 0
        ttk.Label(main, text="Тема (light/dark):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.theme_entry = ttk.Entry(main, width=30)
        self.theme_entry.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1

        ttk.Label(main, text="Показывать панель COM (0/1):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.com_toolbar_entry = ttk.Entry(main, width=30)
        self.com_toolbar_entry.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1

        ttk.Label(main, text="Время запуска таймера (ЧЧ:ММ):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.timer_start_entry = ttk.Entry(main, width=30)
        self.timer_start_entry.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1

        ttk.Label(main, text="Интервал таймера (число):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.timer_interval_entry = ttk.Entry(main, width=30)
        self.timer_interval_entry.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1

        ttk.Label(main, text="Единица интервала (sec/min/hour):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.timer_unit_entry = ttk.Entry(main, width=30)
        self.timer_unit_entry.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1

        ttk.Label(main, text="Показывать обратный отсчёт (0/1):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.show_countdown_entry = ttk.Entry(main, width=30)
        self.show_countdown_entry.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1

        ttk.Label(main, text="Шаг обновления таймера (число):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.countdown_step_entry = ttk.Entry(main, width=30)
        self.countdown_step_entry.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1

        ttk.Label(main, text="Автосохранение логов (0/1):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.auto_save_log_entry = ttk.Entry(main, width=30)
        self.auto_save_log_entry.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1

        ttk.Label(main, text="Каталог сохранения логов:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.log_dir_entry = ttk.Entry(main, width=30)
        self.log_dir_entry.grid(row=row, column=1, sticky=tk.W, padx=10)
        row += 1

        # Кнопки
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Сохранить", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.RIGHT)

    def _load_settings(self):
        settings = self.db.get_settings()
        if settings:
            self.theme_entry.insert(0, settings.get('theme') or '')
            self.com_toolbar_entry.insert(0, str(settings.get('show_com_toolbar') or ''))
            self.timer_start_entry.insert(0, settings.get('timer_start_at') or '')
            self.timer_interval_entry.insert(0, str(settings.get('timer_interval') or ''))
            self.timer_unit_entry.insert(0, settings.get('timer_unit') or '')
            self.show_countdown_entry.insert(0, str(settings.get('show_countdown') or ''))
            self.countdown_step_entry.insert(0, str(settings.get('countdown_step') or ''))
            self.auto_save_log_entry.insert(0, str(settings.get('auto_save_log') or ''))
            self.log_dir_entry.insert(0, settings.get('log_save_dir') or '')

    def _save(self):
        data = {
            'id': 1, 
            'theme': self.theme_entry.get().strip(),
            'show_com_toolbar': self._to_int_or_none(self.com_toolbar_entry.get()),
            'timer_start_at': self.timer_start_entry.get().strip(),
            'timer_interval': self._to_int_or_none(self.timer_interval_entry.get()),
            'timer_unit': self.timer_unit_entry.get().strip(),
            'show_countdown': self._to_int_or_none(self.show_countdown_entry.get()),
            'countdown_step': self._to_int_or_none(self.countdown_step_entry.get()),
            'auto_save_log': self._to_int_or_none(self.auto_save_log_entry.get()),
            'log_save_dir': self.log_dir_entry.get().strip()
        }
        self.db.update_settings(data)
        messagebox.showinfo("Успех", "Настройки сохранены")
        self.destroy()

    @staticmethod
    def _to_int_or_none(value):
        val = value.strip()
        if val == '':
            return None
        try:
            return int(val)
        except ValueError:
            return None

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")