import tkinter as tk
from tkinter import ttk, Toplevel
from tkinter import messagebox

from config import config, save_config


class MemorySettingsDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Настройки памяти")
        self.geometry("450x350")
        self.resizable(False, False)

        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="ОЗУ (внешнее)").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0,5))
        ttk.Label(frame, text="Начальный адрес:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ram_start_entry = ttk.Entry(frame, width=20)
        self.ram_start_entry.insert(0, f"0x{config['ram_start']:08X}")
        self.ram_start_entry.grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(frame, text="Конечный адрес:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.ram_end_entry = ttk.Entry(frame, width=20)
        self.ram_end_entry.insert(0, f"0x{config['ram_end']:08X}")
        self.ram_end_entry.grid(row=2, column=1, sticky=tk.W, pady=2)

        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=10)

        ttk.Label(frame, text="ПЗУ").grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0,5))
        ttk.Label(frame, text="Начальный адрес:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.rom_start_entry = ttk.Entry(frame, width=20)
        self.rom_start_entry.insert(0, f"0x{config['rom_start']:08X}")
        self.rom_start_entry.grid(row=5, column=1, sticky=tk.W, pady=2)

        ttk.Label(frame, text="Конечный адрес:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.rom_end_entry = ttk.Entry(frame, width=20)
        self.rom_end_entry.insert(0, f"0x{config['rom_end']:08X}")
        self.rom_end_entry.grid(row=6, column=1, sticky=tk.W, pady=2)

        ttk.Label(frame, text="Ожидаемая CRC (hex, опционально):").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.crc_entry = ttk.Entry(frame, width=20)
        if config.get("expected_crc") is not None:
            self.crc_entry.insert(0, f"{config['expected_crc']:08X}")
        self.crc_entry.grid(row=7, column=1, sticky=tk.W, pady=2)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.transient(parent)
        self.grab_set()

    def on_ok(self):
        try:
            ram_start = int(self.ram_start_entry.get(), 16)
            ram_end   = int(self.ram_end_entry.get(), 16)
            rom_start = int(self.rom_start_entry.get(), 16)
            rom_end   = int(self.rom_end_entry.get(), 16)
            crc_text = self.crc_entry.get().strip()
            expected_crc = int(crc_text, 16) if crc_text else None
            if ram_start > ram_end or rom_start > rom_end:
                raise ValueError("Начальный адрес больше конечного")
            config.update({
                "ram_start": ram_start,
                "ram_end": ram_end,
                "rom_start": rom_start,
                "rom_end": rom_end,
                "expected_crc": expected_crc
            })
            save_config(config)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {e}")