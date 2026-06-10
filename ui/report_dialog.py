import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.report_generator import ReportGenerator
import smtplib
from email.message import EmailMessage

class ReportDialog(tk.Toplevel):
    def __init__(self, parent, last_results):
        super().__init__(parent)
        self.parent = parent
        self.last_results = last_results
        self.title("Создание отчёта")
        self.geometry("500x450")
        self.resizable(True, True)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="Параметры отчёта", font=("Arial", 12, "bold")).pack(pady=(0,10))
        path_frame = ttk.LabelFrame(main_frame, text="Путь сохранения", padding="10")
        path_frame.pack(fill=tk.X, pady=5)

        self.path_var = tk.StringVar(value="report.docx")
        ttk.Entry(path_frame, textvariable=self.path_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="Обзор...", command=self.choose_path).pack(side=tk.LEFT)

        
        data_frame = ttk.LabelFrame(main_frame, text="Данные для отчёта", padding="10")
        data_frame.pack(fill=tk.X, pady=5)

        self.include_ram = tk.BooleanVar(value=True)
        self.include_rom = tk.BooleanVar(value=True)
        self.include_exc = tk.BooleanVar(value=True)
        self.include_summary = tk.BooleanVar(value=True)

        ttk.Checkbutton(data_frame, text="Результаты теста ОЗУ", variable=self.include_ram).pack(anchor=tk.W)
        ttk.Checkbutton(data_frame, text="Результаты теста ПЗУ", variable=self.include_rom).pack(anchor=tk.W)
        ttk.Checkbutton(data_frame, text="Результаты тестов исключений", variable=self.include_exc).pack(anchor=tk.W)
        ttk.Checkbutton(data_frame, text="Общая сводка", variable=self.include_summary).pack(anchor=tk.W)

        
        comment_frame = ttk.LabelFrame(main_frame, text="Комментарий (опционально)", padding="10")
        comment_frame.pack(fill=tk.X, pady=5)

        self.comment_text = tk.Text(comment_frame, height=4, width=50)
        self.comment_text.pack(fill=tk.X)

        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)

        ttk.Button(btn_frame, text="Создать отчёт", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        
        email_frame = ttk.LabelFrame(main_frame, text="Отправка отчёта", padding="10")
        email_frame.pack(fill=tk.X, pady=5)

        ttk.Label(email_frame, text="Email получателя:").pack(anchor=tk.W)

        self.email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.email_var, width=50).pack(fill=tk.X, pady=5)

        self.send_email_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            email_frame,
            text="Отправить отчёт после создания",
            variable=self.send_email_var
        ).pack(anchor=tk.W)

    def choose_path(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word documents", "*.docx"), ("All files", "*.*")]
        )
        if file_path:
            self.path_var.set(file_path)

    def generate_report(self):
        path = self.path_var.get()
        if not path:
            messagebox.showerror("Ошибка", "Укажите путь для сохранения отчёта")
            return

        
        data = {
            "include_ram": self.include_ram.get(),
            "include_rom": self.include_rom.get(),
            "include_exc": self.include_exc.get(),
            "include_summary": self.include_summary.get(),
            "comment": self.comment_text.get("1.0", tk.END).strip(),
            "results": self.last_results
        }

        try:
            ReportGenerator.generate(path, data)

            
            if self.send_email_var.get():

                recipient = self.email_var.get().strip()

                if not recipient:
                    messagebox.showerror(
                        "Ошибка",
                        "Укажите email получателя"
                    )
                    return

                try:
                    self.send_report_email(path, recipient)

                    messagebox.showinfo(
                        "Успех",
                        f"Отчёт сохранён и отправлен:\n{recipient}"
                    )

                except Exception as e:
                    messagebox.showerror(
                        "Ошибка отправки",
                        str(e)
                    )
                    return

            else:
                messagebox.showinfo(
                    "Успех",
                    f"Отчёт сохранён в {path}"
                )

            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать отчёт: {e}")
            
    def send_report_email(self, filepath, recipient):
        sender_email = "your_email@gmail.com"
        sender_password = "your_app_password"

        msg = EmailMessage()
        msg["Subject"] = "Отчёт тестирования"
        msg["From"] = sender_email
        msg["To"] = recipient

        msg.set_content("Во вложении находится отчёт тестирования.")

        with open(filepath, "rb") as f:
            file_data = f.read()
            file_name = filepath.split("/")[-1]

        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=file_name
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)