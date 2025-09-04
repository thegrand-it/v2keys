import tkinter as tk
from gui import VPNGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = VPNGUI(root)
    root.mainloop()