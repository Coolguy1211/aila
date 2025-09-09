import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional


class AilaGUI:
    """Minimal Tkinter-based GUI backend for Aila programs."""

    def __init__(self) -> None:
        self.root: Optional[tk.Tk] = None
        self._inputs: list[tk.Entry] = []
        self._labels: list[tk.Label] = []
        self._buttons: list[tk.Button] = []

    def create_window(self, title: str = "Aila Window") -> None:
        if self.root is None:
            self.root = tk.Tk()
            self.root.title(title)
        else:
            self.root.title(title)

    def label(self, text: str) -> None:
        if not self.root:
            raise RuntimeError("Window not created. Call create_window first.")
        lbl = tk.Label(self.root, text=text)
        lbl.pack(padx=8, pady=4, anchor="w")
        self._labels.append(lbl)

    def input(self, default_text: str = "") -> tk.Entry:
        if not self.root:
            raise RuntimeError("Window not created. Call create_window first.")
        entry = tk.Entry(self.root)
        if default_text:
            entry.insert(0, default_text)
        entry.pack(fill="x", padx=8, pady=4)
        self._inputs.append(entry)
        return entry

    def button(self, text: str, on_click: Optional[Callable[[], None]] = None) -> None:
        if not self.root:
            raise RuntimeError("Window not created. Call create_window first.")
        btn = tk.Button(self.root, text=text, command=on_click)
        btn.pack(padx=8, pady=4)
        self._buttons.append(btn)

    def show(self, text: str) -> None:
        messagebox.showinfo("Aila", text)

    def close(self) -> None:
        if self.root:
            self.root.destroy()
            self.root = None

    def start(self) -> None:
        if self.root:
            self.root.mainloop()


