from tkinter import ttk, messagebox
from ttkthemes import ThemedStyle
from config import config, save_config

class ThemeManager:
    def __init__(self, parent):
        self.parent = parent
        self.style = ThemedStyle(parent)
        self.current_theme = config.get("theme", "arc")
        self.apply_theme(self.current_theme)
        
    def apply_theme(self, theme):
        try:
            if theme == "dark_custom":
                self._apply_dark_theme()
            else:
                self.style.theme_use(theme)
            config["theme"] = theme
            save_config(config)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить тему: {e}")
            
    def _apply_dark_theme(self):
        style = ttk.Style(self.parent)
        style.theme_use("clam")
        bg = "#2b2b2b"
        fg = "#ffffff"
        entry_bg = "#3c3f41"
        select_bg = "#4e5254"

        self.parent.configure(bg=bg)
        style.configure(".", background=bg, foreground=fg, fieldbackground=entry_bg)
        style.configure("TNotebook", background=bg)
        style.configure("TProgressbar", troughcolor=entry_bg, background="#6a9fb5")
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=entry_bg, foreground=fg)
        style.configure("TCheckbutton", background=bg, foreground=fg)
        style.configure("TLabelFrame", background=bg, foreground=fg)
        style.configure("TLabelFrame.Label", background=bg, foreground=fg)
        style.configure("TEntry", fieldbackground=entry_bg, foreground=fg)
        style.configure("TCombobox", fieldbackground=entry_bg, foreground=fg)
        style.map("TButton", background=[("active", select_bg)])