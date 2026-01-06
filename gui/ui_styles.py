import tkinter as tk
from tkinter import ttk

# GLOBAL CONSTANTS (Restored for MainWindow compatibility)
BG_DARK = "#0a0a0a"
BG_PANEL = "#111111"
ACCENT = "#00ff9d"
TEXT_MAIN = "#ffffff"
TEXT_DIM = "#888888"

def apply_styles(root=None):
    """
    Styling helper.

    Accepts optional `root` so it can be called as:
      apply_styles()  OR  apply_styles(root)

    (We don't actually need root to configure ttk styles.)
    """
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "Treeview",
        background=BG_PANEL,
        foreground=TEXT_MAIN,
        fieldbackground=BG_PANEL,
        borderwidth=0,
        rowheight=28,
        font=("Segoe UI", 10),
    )

    style.map(
        "Treeview",
        foreground=[("selected", "#000000")],
        background=[("selected", ACCENT)],
    )

    style.configure(
        "Treeview.Heading",
        background="#333333",
        foreground="#ffffff",
        relief="flat",
        font=("Segoe UI", 10, "bold"),
    )

    style.configure(
        "TProgressbar",
        thickness=10,
        troughcolor="#111",
        background=ACCENT,
    )
