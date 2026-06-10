import tkinter as tk
from tkinter import ttk

import serial
import serial.tools.list_ports

from tkinter import Toplevel
from config import config, save_config


class ComSettingsDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Параметры COM порта")
        self.geometry("480x420")
        self.resizable(True, True)
        self.parent = parent
        self.transient(parent)
        self.grab_set()

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        settings_frame = ttk.LabelFrame(main_frame, text="Настройки последовательного порта", padding="10")
        settings_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(settings_frame, text="Порт:", anchor=tk.E).grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.port_var = tk.StringVar(value=config.get("com_port", ""))
        self.port_combo = ttk.Combobox(settings_frame, textvariable=self.port_var, state="readonly", width=20)
        self.port_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.refresh_ports()
        ttk.Button(settings_frame, text="Обновить", command=self.refresh_ports).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(settings_frame, text="Скорость (бит/с):", anchor=tk.E).grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.baud_var = tk.IntVar(value=config.get("com_baudrate", 115200))
        baud_combo = ttk.Combobox(settings_frame, textvariable=self.baud_var,
                                  values=[9600, 14400, 19200, 38400, 57600, 115200],
                                  state="readonly", width=18)
        baud_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(settings_frame, text="Бит данных:", anchor=tk.E).grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.databits_var = tk.IntVar(value=config.get("com_data_bits", 8))
        databits_combo = ttk.Combobox(settings_frame, textvariable=self.databits_var,
                                      values=[5, 6, 7, 8], state="readonly", width=18)
        databits_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        
        ttk.Label(settings_frame, text="Стоп-биты:", anchor=tk.E).grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        self.stopbits_var = tk.StringVar(value=str(config.get("com_stop_bits", 1)))
        stopbits_combo = ttk.Combobox(settings_frame, textvariable=self.stopbits_var,
                                      values=["1", "1.5", "2"], state="readonly", width=18)
        stopbits_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(settings_frame, text="Управление потоком:", anchor=tk.E).grid(row=5, column=0, sticky=tk.E, padx=5, pady=5)
        self.flow_var = tk.IntVar(value=config.get("com_flow_ctrl", 0))
        flow_combo = ttk.Combobox(settings_frame, textvariable=self.flow_var,
                                  values=["Нет", "Аппаратное (RTS/CTS)"], state="readonly", width=18)
        flow_combo.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)

        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Применить", command=self.on_apply).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.destroy())

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])

    def _save_config(self):
        stop_map = {"1": 1, "1.5": 1.5, "2": 2}
        config["com_port"] = self.port_var.get()
        config["com_baudrate"] = self.baud_var.get()
        config["com_data_bits"] = self.databits_var.get()
        config["com_stop_bits"] = stop_map.get(self.stopbits_var.get(), 1)
        config["com_parity"] = "N"   
        config["com_flow_ctrl"] = 0 if self.flow_var.get() == "Нет" else 1
        save_config(config)

    def on_apply(self):
        self._save_config()

    def on_ok(self):
        self._save_config()
        self.destroy()