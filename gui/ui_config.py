import tkinter as tk
from tkinter import ttk
from gui.ui_styles import BG_PANEL, ACCENT, BG_DARK

class ConfigWindow(tk.Toplevel):
    def __init__(self, parent, t_config):
        super().__init__(parent)
        self.title("ENGINE CONFIGURATION")
        self.geometry("450x550")
        self.configure(bg=BG_DARK)
        self.t_config = t_config
        self.resizable(False, False)
        
        # Header
        tk.Label(self, text="ENGINE PARAMETERS", font=("Impact", 16), bg="#222", fg=ACCENT).pack(fill="x", pady=(0,15))

        # 1. THREADING
        f_thr = tk.LabelFrame(self, text=" MULTI-THREADING ", bg=BG_DARK, fg="white", padx=10, pady=10)
        f_thr.pack(fill="x", padx=15, pady=5)
        tk.Label(f_thr, text="Max Parallel Streams:", bg=BG_DARK, fg="gray").pack(anchor="w")
        self.thr_val = tk.StringVar(value=str(t_config.get("starting_threads", 8)))
        ttk.Combobox(f_thr, textvariable=self.thr_val, values=["1", "2", "4", "8", "16", "32"]).pack(fill="x")

        # 2. I/O BUFFERS (HDD vs SSD tuning)
        f_io = tk.LabelFrame(self, text=" I/O PERFORMANCE ", bg=BG_DARK, fg="white", padx=10, pady=10)
        f_io.pack(fill="x", padx=15, pady=5)
        tk.Label(f_io, text="Read Buffer Size (MB):", bg=BG_DARK, fg="gray").pack(anchor="w")
        self.buf_val = tk.StringVar(value="8")
        ttk.Combobox(f_io, textvariable=self.buf_val, values=["1", "4", "8", "16", "32", "64"]).pack(fill="x")

        # 3. NETWORK / GEEKLINK
        f_net = tk.LabelFrame(self, text=" NETWORK TIMEOUTS ", bg=BG_DARK, fg="white", padx=10, pady=10)
        f_net.pack(fill="x", padx=15, pady=5)
        tk.Label(f_net, text="Connection Timeout (s):", bg=BG_DARK, fg="gray").pack(anchor="w")
        self.net_val = tk.Scale(f_net, from_=5, to=60, orient="horizontal", bg=BG_DARK, fg="white", highlightthickness=0)
        self.net_val.set(30)
        self.net_val.pack(fill="x")

        # 4. SAVE BUTTON
        tk.Button(self, text="APPLY & SAVE", bg=ACCENT, fg="black", font=("Impact", 14), command=self.save_and_close).pack(pady=30, padx=20, fill="x")

    def save_and_close(self):
        # Update the live config object
        self.t_config.set("starting_threads", int(self.thr_val.get()))
        self.t_config.set("buffer_size_mb", int(self.buf_val.get()))
        # Future: Write to JSON file here
        self.destroy()