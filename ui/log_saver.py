from tkinter import filedialog, messagebox
from datetime import datetime
import os


class LogSaver:
    @staticmethod
    def save_log(output_pane, parent, cell_names=None):

        save_dir = filedialog.askdirectory(
            parent=parent,
            title="Выберите папку для сохранения"
        )

        if not save_dir:
            return False

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:

            log_text = output_pane.get_all_text()
            
            if cell_names:

                unique_cells = list(dict.fromkeys(cell_names))

                safe_cells = []

                for cell in unique_cells:

                    safe_name = cell.strip()

                    for ch in r'\/:*?"<>|':
                        safe_name = safe_name.replace(ch, "_")

                    safe_cells.append(safe_name)

                cells_part = "_".join(safe_cells)

                filename = f"{cells_part}_{timestamp}.txt"

                
                for cell_name in safe_cells:

                    cell_dir = os.path.join(save_dir, cell_name)

                    os.makedirs(cell_dir, exist_ok=True)

                    file_path = os.path.join(cell_dir, filename)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(log_text)

            else:

                os.makedirs(save_dir, exist_ok=True)

                filename = f"test_log_{timestamp}.txt"

                file_path = os.path.join(save_dir, filename)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_text)

            return True

        except Exception as e:

            messagebox.showerror(
                "Ошибка",
                f"Не удалось сохранить файл:\n{e}"
            )

            return False

    @staticmethod
    def save_log_auto(output_pane, save_dir, cell_names=None):

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:

            log_text = output_pane.get_all_text()

            if cell_names:

                unique_cells = list(dict.fromkeys(cell_names))

                
                safe_cells = []

                for cell in unique_cells:

                    safe_name = cell

                    for ch in r'\/:*?"<>|':
                        safe_name = safe_name.replace(ch, "_")

                    safe_cells.append(safe_name)

                cells_part = "_".join(safe_cells)

                filename = f"{cells_part}_{timestamp}.txt"

                for cell_name in safe_cells:
     
                    cell_dir = os.path.join(save_dir, cell_name)

                    os.makedirs(cell_dir, exist_ok=True)

                    file_path = os.path.join(cell_dir, filename)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(log_text)

            else:

                os.makedirs(save_dir, exist_ok=True)

                filename = f"test_log_{timestamp}.txt"

                file_path = os.path.join(save_dir, filename)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_text)

            return True

        except Exception as e:

            messagebox.showerror(
                "Ошибка",
                f"Не удалось сохранить файл:\n{e}"
            )

            return False