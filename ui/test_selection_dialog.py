import tkinter as tk
from tkinter import ttk, Toplevel

from config import config, save_config

from ui.tests_definitions import ALL_TESTS

class TestSelectionDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Выбор отображаемых тестов")
        self.geometry("700x550")
        self.resizable(True, True)
        self.parent = parent
        self.transient(parent)
        self.grab_set()

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Отметьте тесты, которые должны отображаться на главном окне:",
                  font=("", 10, "bold")).pack(anchor=tk.W, pady=(0,10))

        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        categories = {}
        for test in ALL_TESTS:
            categories.setdefault(test["category"], []).append(test)

        self.test_vars = {}
        for cat, tests in categories.items():
            group = ttk.LabelFrame(scrollable_frame, text=cat, padding="5")
            group.pack(fill=tk.X, padx=5, pady=5)

            for test in tests:
                var = tk.BooleanVar(value=test["id"] in config.get("selected_tests", []))
                cb = ttk.Checkbutton(group, text=test["name"], variable=var)
                cb.pack(anchor=tk.W, padx=10, pady=2)
                if not test["implemented"]:
                    cb.config(state=tk.DISABLED)
                    ttk.Label(group, text="(в разработке)", foreground="gray").pack(anchor=tk.W, padx=30)
                self.test_vars[test["id"]] = var

        btn_frame_all = ttk.Frame(scrollable_frame)
        btn_frame_all.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame_all, text="Выбрать все реализованные",
                   command=self.select_all_implemented).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_all, text="Очистить все",
                   command=self.clear_all).pack(side=tk.LEFT, padx=5)

        sep = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=10)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.RIGHT, padx=5)

        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.destroy())

    def select_all_implemented(self):
        for test in ALL_TESTS:
            if test["implemented"]:
                self.test_vars[test["id"]].set(True)

    def clear_all(self):
        for var in self.test_vars.values():
            var.set(False)

    def on_ok(self):
        selected = [tid for tid, var in self.test_vars.items() if var.get()]
        config["selected_tests"] = selected
        save_config(config)
        self.parent.refresh_test_panel()
        self.destroy()