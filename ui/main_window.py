import tkinter as tk
from tkinter import BooleanVar, Menu, messagebox, ttk

from config import config, save_config
from core.cell_db import CellDB
from core.report_generator import ReportGenerator
from core.timer_manager import TimerManager
from ui.cell_dialog import CellDialog
from ui.com_dialog import ComSettingsDialog
from ui.commands_dialog import CommandsDialog
from ui.helper import Helper
from ui.log_saver import LogSaver
from ui.memory_dialog import MemorySettingsDialog
from ui.output_pane import OutputPane
from ui.port_manager import PortManager
from ui.report_dialog import ReportDialog
from ui.save_settings_dialog import SaveSettingsDialog
from ui.scheduler import TestScheduler
from ui.test_runner import TestRunner
from ui.test_selection_dialog import TestSelectionDialog
from ui.tests_definitions import ALL_TESTS
from ui.theme_manager import ThemeManager
from ui.timer_settings_dialog import TimerSettingsDialog


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Тесты: ОЗУ, ПЗУ, CPU/FPU")
        self.geometry("900x700")
        self.resizable(True, True)

        self.comm = None
        self.testing_active = False
        self.output_detached = False
        self.output_window = None

        
        self.cell_db = CellDB()
        self.current_cell_id = config.get("selected_cell_id", None)

        
        if self.current_cell_id:
            if not self.cell_db.get_cell_name(self.current_cell_id):
                self.current_cell_id = None

        self.last_ram_errors = 0
        self.last_ram_details = []
        self.last_rom_errors = 0
        self.last_rom_crc = 0
        self.last_exc_errors = 0
        self.last_exc_details = []
        self.total_cycles = 0
        self.total_all_errors = 0
        
        self.statusbar = ttk.Frame(self, relief=tk.SUNKEN)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(self.statusbar, text="Порт закрыт", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self._create_output_pane(self)

        self.scheduler = TestScheduler(self.run_tests)
        self.port_manager = PortManager(self, self.output, self.status_label)
        self.theme_manager = ThemeManager(self)
        self.timer_manager = TimerManager(self, self.scheduler, self._log_message)
        self.test_runner = TestRunner(
            self, self.comm, self.output, self._progress_callback, self._log_message
        )

        self._create_menu()

        self._create_com_toolbar()
        self.port_manager.refresh_ports(self.port_combo)

        self.test_frame = ttk.LabelFrame(self, text="Выберите тесты")
        self.test_frame.pack(fill=tk.X, padx=10, pady=10)
        self.test_checkbuttons = []
        self.refresh_test_panel()

        self._create_control_panel()

        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode="determinate")
        self.progress.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.progress_label = ttk.Label(self, text="")
        self.progress_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5)

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.used_cells_in_session = []

        if config.get("com_port"):
            self.port_combo.set(config["com_port"])

        self.after(100, self.update_console)

    def _create_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)

        app_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Приложение", menu=app_menu)
        app_menu.add_command(label="COM порт", command=self.open_com_settings)
        app_menu.add_command(label="Адреса памяти", command=self.open_mem_settings)
        app_menu.add_command(label="Выбор тестов", command=self.open_test_selection)
        app_menu.add_separator()
        app_menu.add_command(label="Выход", command=self.quit)

        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Создать отчёт", command=self.generate_report)

        tools_menu.add_separator()

        tools_menu.add_command(
            label="Команды монитора", command=self.open_commands_dialog
        )

        tools_menu.add_separator()
        tools_menu.add_command(
            label="Настройки сохранения", command=self.open_save_settings
        )

        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        self.theme_var = tk.StringVar(value=config.get("theme", "arc"))
        self.show_com_toolbar_var = BooleanVar(
            value=config.get("show_com_toolbar", True)
        )
        view_menu.add_checkbutton(
            label="Панель инструментов COM-порта",
            variable=self.show_com_toolbar_var,
            command=self.toggle_com_toolbar,
        )
        view_menu.add_command(
            label="Окно вывода (отдельно)", command=self.toggle_output_window
        )

        
        themes_menu = Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Цветовая тема", menu=themes_menu)
        themes = ["arc", "plastik", "equilux", "radiance", "scidblue", "dark_custom"]
        for theme in themes:
            themes_menu.add_radiobutton(
                label=theme,
                variable=self.theme_var,
                value=theme,
                command=self.change_theme,
            )

        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.about)
        help_menu.add_command(label="Помощь", command=self.helper)

        self.console_frame = ttk.LabelFrame(self, text="Консоль монитора")

        self.console_frame.pack(fill=tk.X, padx=10, pady=5)

        self.command_var = tk.StringVar()

        self.command_entry = ttk.Entry(
            self.console_frame, textvariable=self.command_var
        )

        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.send_button = ttk.Button(
            self.console_frame, text="Отправить", command=self.send_user_command
        )

        self.commands_button = ttk.Button(
            self.console_frame, text="Команды", command=self.open_commands_dialog
        )

        self.commands_button.pack(side=tk.LEFT, padx=5)

        self.send_button.pack(side=tk.LEFT, padx=5)
        self.command_entry.bind("<Return>", lambda e: self.send_user_command())

        self.bind_all("<Control-Key>", self.handle_ctrl_keys)

    def handle_ctrl_keys(self, event):

        if not self.comm:
            return

        if not (event.state & 0x4):
            return

        key = event.keysym.upper()

        if len(key) != 1 or not ("A" <= key <= "Z"):
            return

        code = ord(key) - ord("A") + 1

        try:
            self.comm.write_raw(bytes([code]))

            self.output.print_message(f"> CTRL+{key} (0x{code:02X})", "blue")

        except Exception as e:
            self.output.print_message(str(e), "red")

        return "break"

    def send_saved_command(self, command, is_ctrl):

        if not self.comm:
            return

        try:
            if is_ctrl:
                code = ord(command.upper()) - ord("A") + 1

                self.comm.write_raw(bytes([code]))

                self.output.print_message(f"> CTRL+{command.upper()}", "blue")

            else:
                self.comm.send_command(command)

                self.output.print_message(f"> {command}", "blue")

        except Exception as e:
            self.output.print_message(str(e), "red")

    def open_commands_dialog(self):
        dlg = CommandsDialog(self)
        self.wait_window(dlg)

    def send_user_command(self):

        if not self.comm:
            return

        cmd = self.command_var.get().strip()

        if not cmd:
            return

        try:
            self.comm.send_command(cmd)

            self.output.print_message(f"> {cmd}", "blue")

            self.command_var.set("")

        except Exception as e:
            self.output.print_message(str(e), "red")

    def update_console(self):

        try:
            if self.comm:
                text = self.comm.get_console_text()

                if text:
                    for line in text.splitlines():
                        self.output.print_message(line, "green")

        except Exception:
            pass

        self.after(100, self.update_console)

    def _create_com_toolbar(self):
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, pady=2, padx=5)

        self.com_label = ttk.Label(self.toolbar, text="COM-порт:")
        self.port_combo = ttk.Combobox(self.toolbar, width=8, state="readonly")
        self.btn_refresh = ttk.Button(
            self.toolbar,
            text="Обновить",
            command=lambda: self.port_manager.refresh_ports(self.port_combo),
        )
        self.btn_open = ttk.Button(
            self.toolbar, text="Открыть порт", command=self.open_port
        )
        self.btn_close = ttk.Button(
            self.toolbar,
            text="Закрыть порт",
            command=self.close_port,
            state=tk.DISABLED,
        )
        self.sep = ttk.Separator(self.toolbar, orient=tk.VERTICAL)

        self.cell_label = ttk.Label(self.toolbar, text="Тип ячейки:")
        self.cell_combo = ttk.Combobox(self.toolbar, width=15, state="readonly")
        self.cell_combo.bind("<<ComboboxSelected>>", self.on_cell_changed)
        self.btn_add_cell = ttk.Button(
            self.toolbar, text="Изменить", command=self.add_cell
        )

        self.apply_com_toolbar_visibility()

        self._load_cell_list()

    def apply_com_toolbar_visibility(self):
        show = config.get("show_com_toolbar", True)
        for w in (
            self.com_label,
            self.port_combo,
            self.btn_refresh,
            self.btn_open,
            self.btn_close,
            self.sep,
            self.cell_label,
            self.cell_combo,
            self.btn_add_cell,
        ):
            w.pack_forget()
        if show:
            self.com_label.pack(side=tk.LEFT, padx=5)
            self.port_combo.pack(side=tk.LEFT, padx=2)
            self.btn_refresh.pack(side=tk.LEFT, padx=2)
            self.btn_open.pack(side=tk.LEFT, padx=2)
            self.btn_close.pack(side=tk.LEFT, padx=2)
            self.sep.pack(side=tk.LEFT, fill=tk.Y, padx=10)
            self.cell_label.pack(side=tk.LEFT, padx=5)
            self.cell_combo.pack(side=tk.LEFT, padx=2)
            self.btn_add_cell.pack(side=tk.LEFT, padx=2)

    def _create_control_panel(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)

        self.btn_run = ttk.Button(btn_frame, text="Запустить", command=self.run_tests)

        self.btn_run.pack(side=tk.LEFT, padx=10)
        self.btn_stop = ttk.Button(
            btn_frame, text="Прервать", command=self.stop_tests, state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        ttk.Label(btn_frame, text="Интервал:").pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.IntVar(value=10)
        ttk.Entry(btn_frame, width=5, textvariable=self.interval_var).pack(side=tk.LEFT)
        self.unit_var = tk.StringVar(value="seconds")
        unit_menu = ttk.Combobox(
            btn_frame,
            textvariable=self.unit_var,
            values=["seconds", "minutes", "hours"],
            width=8,
            state="readonly",
        )
        unit_menu.pack(side=tk.LEFT, padx=5)
        self.btn_start_interval = ttk.Button(
            btn_frame, text="Старт интервал", command=self.start_interval_timer
        )
        self.btn_start_interval.pack(side=tk.LEFT, padx=5)

        ttk.Label(btn_frame, text="Время (HH:MM):").pack(side=tk.LEFT, padx=5)
        self.time_var = tk.StringVar(value="12:00")
        ttk.Entry(btn_frame, width=6, textvariable=self.time_var).pack(side=tk.LEFT)
        self.btn_start_time = ttk.Button(
            btn_frame, text="Старт по времени", command=self.start_time_timer
        )
        self.btn_start_time.pack(side=tk.LEFT, padx=5)

        self.btn_stop_timer = ttk.Button(
            btn_frame, text="Стоп таймер", command=self.stop_timer
        )
        self.btn_stop_timer.pack(side=tk.LEFT, padx=5)
        self.btn_auto_stop = ttk.Button(
            btn_frame, text="Авто Стоп", command=self.stop_auto_tests
        )
        self.btn_auto_stop.pack(side=tk.LEFT, padx=5)

        self.cycle_var = tk.BooleanVar(value=config.get("cycle_tests", False))
        ttk.Checkbutton(
            btn_frame, text="Повторять в цикле", variable=self.cycle_var
        ).pack(side=tk.LEFT, padx=20)
        self.cycle_label = ttk.Label(btn_frame, text="")
        self.cycle_label.pack(side=tk.LEFT, padx=10)

        self.btn_timer_cfg = ttk.Button(
            btn_frame, text="Настроить таймер ⏱", command=self.open_timer_settings
        )
        self.btn_timer_cfg.pack(side=tk.LEFT, padx=10)

    def _create_output_pane(self, parent):
        self.output = OutputPane(parent)
        self.output.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=5)

    def open_port(self):
        if self.port_manager.open_port(
            self.port_combo.get(), config, self.btn_open, self.btn_close
        ):
            self.comm = self.port_manager.comm
            self.test_runner.comm = self.comm

    def close_port(self):
        self.port_manager.close_port(self.btn_open, self.btn_close)
        self.comm = None
        self.test_runner.comm = None

    def run_tests(self):
        selected_name = self.cell_combo.get()

        if selected_name and selected_name not in self.used_cells_in_session:
            self.used_cells_in_session.append(selected_name)
        if self.test_runner.testing_active:
            return
        if not self.port_manager.is_open():
            messagebox.showerror("Ошибка", "COM-порт не открыт")
            return

        selected_ids = config.get("selected_tests", [])
        tests_to_run = []
        for test in ALL_TESTS:
            if test["id"] in selected_ids and test["implemented"]:
                var = getattr(self, f"var_{test['id']}", None)
                if var and var.get():
                    tests_to_run.append(test["id"])
        if not tests_to_run:
            messagebox.showwarning("Внимание", "Не выбран ни один тест.")
            return

        self.btn_run.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.test_runner.start(tests_to_run, self.cycle_var, self._tests_finished)

    def stop_tests(self):
        self.test_runner.stop()

    def _tests_finished(self, total_errors, cycles, ram_err, rom_err, exc_err, crc):
        self.testing_active = False
        self.btn_run.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.progress_label.config(text="")
        if self.cycle_var.get():
            self.cycle_label.config(text="Цикл остановлен")
        else:
            self.cycle_label.config(text="")
        self.last_ram_errors = ram_err
        self.last_rom_errors = rom_err
        self.last_rom_crc = crc
        self.last_exc_errors = exc_err
        self.total_cycles = cycles
        self.total_all_errors = total_errors

    def start_interval_timer(self):
        self.timer_manager.start_interval(self.interval_var.get(), self.unit_var.get())

    def start_time_timer(self):
        self.timer_manager.start_at_time(self.time_var.get())

    def stop_timer(self):
        self.timer_manager.stop()

    def stop_auto_tests(self):
        self.timer_manager.stop()

    def change_theme(self):
        self.theme_manager.apply_theme(self.theme_var.get())

    def open_timer_settings(self):
        dlg = TimerSettingsDialog(self)
        self.wait_window(dlg)

    def toggle_com_toolbar(self):
        config["show_com_toolbar"] = self.show_com_toolbar_var.get()
        save_config(config)
        self.apply_com_toolbar_visibility()

    def refresh_test_panel(self):
        for var, widget in self.test_checkbuttons:
            widget.destroy()
        self.test_checkbuttons.clear()
        selected = config.get("selected_tests", [])
        for test in ALL_TESTS:
            if test["id"] in selected and test["implemented"]:
                var = tk.BooleanVar(value=True)
                cb = ttk.Checkbutton(self.test_frame, text=test["name"], variable=var)
                cb.pack(anchor=tk.W, pady=2)
                self.test_checkbuttons.append((var, cb))
                setattr(self, f"var_{test['id']}", var)

    def open_com_settings(self):
        dlg = ComSettingsDialog(self)
        self.wait_window(dlg)
        if config.get("com_port"):
            self.port_combo.set(config["com_port"])
        self.port_manager.refresh_ports(self.port_combo)

    def open_mem_settings(self):
        dlg = MemorySettingsDialog(self)
        self.wait_window(dlg)

    def open_test_selection(self):
        dlg = TestSelectionDialog(self)
        self.wait_window(dlg)


    def toggle_output_window(self):
        if not self.output_detached:
            self.output.pack_forget()
            self.output_window = tk.Toplevel(self)
            self.output_window.title("Вывод команд")
            self.output_window.geometry("600x400")
            self.output.master = self.output_window
            self.output.pack(fill=tk.BOTH, expand=True)
            self.output_window.protocol("WM_DELETE_WINDOW", self._attach_output_back)
            self.output_detached = True
        else:
            self._attach_output_back()

    def _attach_output_back(self):
        if self.output_window:
            self.output.pack_forget()
            self.output_window.destroy()
            self.output_window = None
        self.output.master = self
        self.output.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=5)
        self.output_detached = False

    def generate_report(self):
        last_results = {
            "ram": {"errors": self.last_ram_errors, "details": self.last_ram_details},
            "rom": {
                "errors": self.last_rom_errors,
                "crc": self.last_rom_crc,
                "expected_crc": config.get("expected_crc"),
            },
            "exc": {"errors": self.last_exc_errors, "details": self.last_exc_details},
            "summary": {
                "cycles": self.total_cycles,
                "total_errors": self.total_all_errors,
            },
        }
        dlg = ReportDialog(self, last_results)
        self.wait_window(dlg)

    def generate_report_document(self, path, data):
        try:
            ReportGenerator.generate(path, data)
            messagebox.showinfo("Успех", f"Отчёт сохранён в {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать отчёт: {e}")

    def _progress_callback(self, percent, status=""):
        self.after(0, lambda: self.progress.configure(value=percent))
        self.after(0, lambda: self.progress_label.config(text=status))

    def _log_message(self, msg, level="info"):
        self.output.print_message(msg, level)

    def about(self):
        messagebox.showinfo(
            "О программе",
            "Версия 1.2\n\n"
            "Тесты:\n"
            "- Внешнее ОЗУ\n"
            "- ПЗУ\n"
            "- Исключения CPU\n"
            "- Исключения FPU\n\n"
            "Подключение к ячейке и работа с тестами происходит, через окно ввода на главном окне\n\n"
            "Работает через COM-порт с монитором ячейки.\n\n"
            "Подробное описание настройки ячеек и описание ПО смотрите на панели "
            "Помощь"
            "",
        )

    def helper(self):
        dlg = Helper(self)
        self.wait_window(dlg)

    def _on_closing(self):

        if config.get("auto_save_log", False):
            save_dir = config.get("log_save_dir", "")
            if save_dir:
                LogSaver.save_log_auto(
                    self.output, save_dir, self.used_cells_in_session
                )
            self.destroy()
        else:
            answer = messagebox.askyesnocancel(
                "Сохранить вывод",
                "Сохранить содержимое панели вывода в текстовый файл?",
            )
            if answer is True:  
                LogSaver.save_log(self.output, self, self.used_cells_in_session)
                self.destroy()
            elif answer is False: 
                self.destroy()
            else:  
                return


    def _load_cell_list(self):

        cells = self.cell_db.get_all_cells()

        self.cell_names = {cell[0]: cell[1] for cell in cells}

        if hasattr(self, "cell_combo"):
            values = [name for _, name, _ in cells]

            values.insert(0, "Выберите ячейку")

            self.cell_combo["values"] = values

            self.cell_combo.set("Выберите ячейку")

            self.current_cell_id = None

    def on_cell_changed(self, event=None):

        selected_name = self.cell_combo.get()

        if selected_name == "Выберите ячейку":
            return

        if not selected_name:
            return

        cell_id = None

        for cid, name in self.cell_names.items():
            if name == selected_name:
                cell_id = cid
                break

        if cell_id is None:
            return

        if cell_id != self.current_cell_id:
            self.current_cell_id = cell_id

            config["selected_cell_id"] = cell_id

            save_config(config)

            msg = f"Смена типа ячейки на '{selected_name}'"

            self.output.print_message(msg, "blue")

            if selected_name not in self.used_cells_in_session:
                self.used_cells_in_session.append(selected_name)

    def add_cell(self):

        old_selected_id = self.current_cell_id

        dlg = CellDialog(self)

        self.wait_window(dlg)

        if dlg.changed:
            self._load_cell_list()

            if dlg.result:
                new_id, new_name = dlg.result

                self.current_cell_id = new_id

                self.cell_combo.set(new_name)

            elif old_selected_id not in self.cell_names:
                if self.cell_names:
                    first_id = next(iter(self.cell_names))

                    self.current_cell_id = first_id

                    self.cell_combo.set(self.cell_names[first_id])

                else:
                    self.current_cell_id = None
                    self.cell_combo.set("")

            config["selected_cell_id"] = self.current_cell_id

            save_config(config)

    def open_save_settings(self):
        dlg = SaveSettingsDialog(self)
        self.wait_window(dlg)