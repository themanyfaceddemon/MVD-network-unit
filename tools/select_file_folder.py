import tkinter as tk
from tkinter import filedialog
from typing import List


class FileManager:
    @staticmethod
    def select_folder(title: str) -> str | None:
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory(title=title)
        return folder_path if folder_path else None

    @staticmethod
    def select_file(
        title: str,
        filetypes: List[tuple] = [("All Files", "*.*")],
    ) -> str | None:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        return file_path if file_path else None

    @staticmethod
    def select_files(
        title: str,
        filetypes: List[tuple] = [("All Files", "*.*")],
    ) -> List[str] | None:
        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames(title=title, filetypes=filetypes)
        return list(file_paths) if file_paths else None
