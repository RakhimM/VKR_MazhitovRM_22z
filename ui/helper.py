import tkinter as tk
from tkinter import ttk


def Helper(self):

    help_win = tk.Toplevel(self)
    help_win.title("Помощь")
    help_win.geometry("900x700")
    help_win.minsize(700, 500)

    notebook = ttk.Notebook(help_win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    sections = {
        "Быстрый старт": """
""",

        "Основное окно": """
""",

        "Поля ввода": """
""",

        "Таймеры": """
""",

        "Меню": """
""",

        "Модальные окна": """
""",

        "Окно вывода": """
В журнале отображаются:

• Отправленные команды
• Ответы устройства
• Результаты тестов
• Ошибки
• Предупреждения
• Служебные сообщения

Для очистки консоли вывода используйте:

Инструменты → Очистить вывод
""",

        "Ошибки": """
"""
    }

    for tab_name, text_content in sections.items():

        frame = ttk.Frame(notebook)
        notebook.add(frame, text=tab_name)

        text_widget = tk.Text(
            frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=text_widget.yview
        )

        text_widget.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        text_widget.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        text_widget.insert(
            tk.END,
            text_content
        )

        text_widget.config(
            state=tk.DISABLED
        )

    btn_frame = ttk.Frame(help_win)
    btn_frame.pack(fill=tk.X, padx=10, pady=5)

    ttk.Button(
        btn_frame,
        text="Закрыть",
        command=help_win.destroy
    ).pack(side=tk.RIGHT)