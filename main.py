"""CardPuter ComboKey XML Editor - Entry Point."""

import tkinter as tk
from app import ComboKeyEditor


def main():
    root = tk.Tk()
    root.configure(bg="#ffffff")
    app = ComboKeyEditor(root)

    # Center window
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    root.mainloop()


if __name__ == "__main__":
    main()
