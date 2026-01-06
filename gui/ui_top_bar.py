import tkinter as tk
from gui.ui_styles import BG_DARK, ACCENT

class TopBarComponent(tk.Frame):
    def __init__(self, parent, dashboard_callback, config_callback):
        super().__init__(parent, bg=BG_DARK, height=60)
        self.pack_propagate(False)
        
        # Branding
        tk.Label(self, text="GEEK SQUAD OS", font=("Impact", 20), bg=BG_DARK, fg="white").pack(side="left", padx=20)
        
        # Actions
        tk.Button(self, text="DASHBOARD 🌐", bg=ACCENT, fg="black", font=("Consolas", 10, "bold"), 
                  command=dashboard_callback).pack(side="right", padx=10)
        tk.Button(self, text="SETTINGS ⚙", bg="#333", fg="white", font=("Consolas", 10), 
                  command=config_callback).pack(side="right", padx=5)