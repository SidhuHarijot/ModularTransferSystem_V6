import tkinter as tk
from tkinter import scrolledtext
import time

class ConsoleComponent(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#050505", height=150, bd=1, relief="solid")
        self.pack_propagate(False)
        
        tk.Label(self, text=" SYSTEM LOG ", bg="#222", fg="gray", font=("Consolas", 8, "bold")).pack(fill="x")
        
        self.text_area = scrolledtext.ScrolledText(self, bg="black", fg="#00ff00", 
                                                   font=("Consolas", 9), state="disabled", bd=0)
        self.text_area.pack(fill="both", expand=True)
        self.log("SYSTEM", "CONSOLE INITIALIZED. READY FOR MISSION.")

    def log(self, level, msg):
        self.text_area.config(state="normal")
        ts = time.strftime('%H:%M:%S')
        self.text_area.insert(tk.END, f"[{ts}] [{level}] {msg}\n")
        self.text_area.see(tk.END)
        self.text_area.config(state="disabled")