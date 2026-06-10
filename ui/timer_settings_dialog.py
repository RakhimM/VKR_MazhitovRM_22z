import tkinter as tk
from tkinter import ttk
from config import config, save_config

class TimerSettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Настройка таймера")
        self.geometry("380x350")
        self.resizable(False, False)
        self.grab_set()

        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        int_frame = ttk.LabelFrame(main_frame, text="Запуск по интервалу", padding="10")
        int_frame.pack(fill=tk.X, pady=5)
        
        self.interval_var = tk.IntVar(value=config.get("timer_interval", 10))
        ttk.Entry(int_frame, width=7, textvariable=self.interval_var).pack(side=tk.LEFT, padx=5)
        
        self.unit_var = tk.StringVar(value=config.get("timer_unit", "minutes"))
        ttk.Combobox(int_frame, textvariable=self.unit_var, values=["seconds", "minutes", "hours"], 
                     width=10, state="readonly").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(int_frame, text="Старт", command=self.start_interval).pack(side=tk.RIGHT)

        time_frame = ttk.LabelFrame(main_frame, text="Запуск в точное время", padding="10")
        time_frame.pack(fill=tk.X, pady=5)
        
        self.time_var = tk.StringVar(value=config.get("timer_start_at", "12:00"))
        ttk.Entry(time_frame, width=10, textvariable=self.time_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(time_frame, text="Старт", command=self.start_at_time).pack(side=tk.RIGHT)

        log_frame = ttk.LabelFrame(main_frame, text="Вывод отсчета в лог", padding="10")
        log_frame.pack(fill=tk.X, pady=5)

        self.show_countdown_var = tk.BooleanVar(value=config.get("show_countdown", True))
        ttk.Checkbutton(log_frame, text="Включить отсчет", variable=self.show_countdown_var).pack(side=tk.LEFT)

        ttk.Label(log_frame, text=" каждые (сек):").pack(side=tk.LEFT)
        self.log_step_var = tk.IntVar(value=config.get("countdown_step", 10))
        ttk.Entry(log_frame, width=5, textvariable=self.log_step_var).pack(side=tk.LEFT, padx=5)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        ttk.Button(bottom_frame, text="Стоп таймер", command=self.stop_timers).pack(side=tk.LEFT)
        ttk.Button(bottom_frame, text="Закрыть", command=self.destroy).pack(side=tk.RIGHT)

    def _save_and_start_monitor(self):
        config["show_countdown"] = self.show_countdown_var.get()
        config["countdown_step"] = self.log_step_var.get()
        save_config(config)

    def start_interval(self):
        val, unit = self.interval_var.get(), self.unit_var.get()
        config["timer_interval"], config["timer_unit"] = val, unit
        self._save_and_start_monitor()
        self.parent.scheduler.start_interval(val, unit)
        self.parent.start_countdown_monitoring()
        self.destroy()

    def start_at_time(self):
        t_str = self.time_var.get()
        config["timer_start_at"] = t_str
        self._save_and_start_monitor()
        self.parent.scheduler.start_at_time(t_str)   # ← ВАЖНО
        self.parent.start_countdown_monitoring()
        self.destroy()

    def stop_timers(self):
        self.parent.scheduler.stop()
        self.destroy()