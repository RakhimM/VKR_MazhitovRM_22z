import tkinter as tk
from tkinter import ttk
from collections import deque

class ColorListBox(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.text = tk.Text(self, wrap=tk.WORD, height=15)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar.set)

        self.text.tag_config("red", foreground="red")
        self.text.tag_config("green", foreground="green")
        self.text.tag_config("blue", foreground="blue")
        self.text.tag_config("black", foreground="black")
        self.text.tag_config("yellow", foreground="orange")  

        self.queue = deque()
        self.after(100, self._process_queue)

        
        self.lines = []  

    def _process_queue(self):
        while self.queue:
            method, args, kwargs = self.queue.popleft()
            method(*args, **kwargs)
        self.after(100, self._process_queue)

    def _add_to_queue(self, method, *args, **kwargs):
        self.queue.append((method, args, kwargs))

    def add_color_item(self, text, color="black"):
        self.text.insert(tk.END, text + "\n")
        
        line_start = f"{self.text.index('end-2c')} linestart"
        line_end = f"{self.text.index('end-1c')} lineend"
        self.text.tag_add(color, line_start, line_end)
        
        self.lines.append((line_start, line_end))
        return len(self.lines) - 1

    def print_string(self, row, dwColor, text):
        if row < 0 or row >= len(self.lines):
            return
        start, end = self.lines[row]
        
        self.text.delete(start, end)
        
        self.text.insert(start, text)
        
        new_end = f"{start} + {len(text)}c"
        self.lines[row] = (start, new_end)
        
        
        tags = self.text.tag_names(start)
        color_tag = next((t for t in tags if t in ("red","green","blue","black","yellow")), "black")
        self.text.tag_add(color_tag, start, new_end)

    def backspace(self, row):
        if row < 0 or row >= len(self.lines):
            return
        start, end = self.lines[row]
        
        current_text = self.text.get(start, end)
        if len(current_text) > 0:
            new_text = current_text[:-1]
            self.print_string(row, 0, new_text)

    def get_count(self):
        return len(self.lines)

    def clear(self):
        self.text.delete("1.0", tk.END)
        self.lines.clear()

class OutputPane(ttk.Frame):
    def __init__(self, parent, language="russian"):
        super().__init__(parent)
        self.language = language  

        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        
        self.messages_frame = ttk.Frame(self.notebook)
        self.service_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.messages_frame, text=self._tr("Messages", "Сообщения"))
        self.notebook.add(self.service_frame, text=self._tr("Service", "Служебные"))

        
        self.message_list = ColorListBox(self.messages_frame)
        self.message_list.pack(fill=tk.BOTH, expand=True)

        self.service_list = ColorListBox(self.service_frame)
        self.service_list.pack(fill=tk.BOTH, expand=True)

        
        self.queue = deque()
        self.after(100, self._process_global_queue)

    def _tr(self, eng, rus):
        return eng if self.language == "english" else rus

    def _process_global_queue(self):
        while self.queue:
            method, args, kwargs = self.queue.popleft()
            method(*args, **kwargs)
        self.after(100, self._process_global_queue)

    def _invoke(self, method, *args, **kwargs):
        self.queue.append((method, args, kwargs))

    

    def print_message(self, text, color="black"):
        return self.message_list.add_color_item(text, color)

    def print_service(self, text, color="black"):
        self.select_tab(1)          
        return self.service_list.add_color_item(text, color)

    def select_tab(self, index):
        self.notebook.select(index)

    def continue_message(self, row, color, text):
        self.message_list.print_string(row, color, text)

    def continue_service(self, row, color, text):
        self.service_list.print_string(row, color, text)

    def bs_message(self, row):
        self.message_list.backspace(row)

    def get_message_count(self):
        return self.message_list.get_count()

    
    def clear_messages(self):
        self.message_list.clear()

    def clear_service(self):
        self.service_list.clear()

    def get_all_text(self, tab=0):
        if tab == 0:
            w = self.message_list.text
        else:
            w = self.service_list.text
        return w.get("1.0", tk.END)
