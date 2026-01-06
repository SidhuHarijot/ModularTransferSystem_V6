import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import time
import shutil

# STYLES
BG_DARK = "#101010"
BG_PANEL = "#1a1a1a"
ACCENT = "#ff3333" # Red for destruction
TEXT_MAIN = "#ffffff"
TEXT_DIM = "#666666"

class IncineratorTool:
    def __init__(self):
        self.name = "🔥 DATA INCINERATOR"
        self.root = None
        self.target_path = None
        self.is_scanning = False
        self.is_burning = False
        self.stop_event = False
        
        # Stats
        self.total_files = 0
        self.total_bytes = 0
        self.deleted_files = 0
        self.deleted_bytes = 0

    def run(self, root_window):
        self.root = tk.Toplevel(root_window)
        self.root.title("INCINERATOR 2.0 // HIGH SPEED DELETION")
        self.root.geometry("600x450")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)
        
        # UI LAYOUT
        self.draw_ui()
        
    def draw_ui(self):
        # HEADER
        hdr = tk.Frame(self.root, bg=BG_DARK)
        hdr.pack(fill="x", padx=20, pady=20)
        tk.Label(hdr, text="DATA INCINERATOR", font=("Impact", 24), bg=BG_DARK, fg=ACCENT).pack(side="left")
        
        # PATH SELECTION
        f_path = tk.Frame(self.root, bg=BG_PANEL, padx=15, pady=15)
        f_path.pack(fill="x", padx=20, pady=10)
        
        tk.Label(f_path, text="TARGET DIRECTORY", font=("Consolas", 10, "bold"), bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w")
        self.lbl_path = tk.Label(f_path, text="NO TARGET SELECTED", font=("Segoe UI", 11), bg="#111", fg="white", width=60, anchor="w", padx=10, relief="flat")
        self.lbl_path.pack(fill="x", pady=5)
        
        btn_browse = tk.Button(f_path, text="SELECT FOLDER", bg="#333", fg="white", font=("Consolas", 10), command=self.browse)
        btn_browse.pack(anchor="e")

        # STATS GRID
        f_stats = tk.Frame(self.root, bg=BG_DARK)
        f_stats.pack(fill="x", padx=20, pady=10)
        
        self.card_files = self.mk_card(f_stats, "FILES FOUND", "0", side="left")
        self.card_size = self.mk_card(f_stats, "TOTAL SIZE", "0.00 GB", side="right")

        # PROGRESS BAR
        self.f_prog = tk.Frame(self.root, bg=BG_DARK)
        self.f_prog.pack(fill="x", padx=20, pady=10)
        
        tk.Label(self.f_prog, text="DESTRUCTION PROGRESS", font=("Consolas", 9), bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w")
        self.pb = ttk.Progressbar(self.f_prog, mode="determinate")
        self.pb.pack(fill="x", pady=5)
        
        self.lbl_status = tk.Label(self.f_prog, text="READY", font=("Consolas", 10), bg=BG_DARK, fg=ACCENT)
        self.lbl_status.pack(anchor="e")

        # ACTION BUTTONS
        f_btn = tk.Frame(self.root, bg=BG_DARK)
        f_btn.pack(fill="x", side="bottom", padx=20, pady=20)
        
        self.btn_burn = tk.Button(f_btn, text="🔥 INCINERATE", bg=ACCENT, fg="black", font=("Impact", 14), state="disabled", command=self.start_burn)
        self.btn_burn.pack(fill="x", ipady=5)

    def mk_card(self, parent, title, val, side):
        f = tk.Frame(parent, bg=BG_PANEL, width=270, height=80)
        f.pack_propagate(False)
        f.pack(side=side)
        
        tk.Label(f, text=title, font=("Consolas", 10, "bold"), bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", padx=15, pady=(15, 5))
        lbl = tk.Label(f, text=val, font=("Segoe UI", 20, "bold"), bg=BG_PANEL, fg="white")
        lbl.pack(anchor="w", padx=15)
        return lbl

    def browse(self):
        p = filedialog.askdirectory()
        if p:
            self.target_path = p
            self.lbl_path.config(text=p)
            self.start_scan()

    # --- FAST SCANNER ENGINE ---
    def start_scan(self):
        self.is_scanning = True
        self.btn_burn.config(state="disabled")
        self.lbl_status.config(text="SCANNING...")
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        self.total_files = 0
        self.total_bytes = 0
        
        # OPTIMIZATION: os.scandir is 10x faster than os.walk because
        # it gets file attributes from the directory entry itself
        # without needing a separate stat() call for every file.
        stack = [self.target_path]
        
        while stack and self.target_path:
            try:
                current_dir = stack.pop()
                with os.scandir(current_dir) as it:
                    for entry in it:
                        if entry.is_file():
                            self.total_files += 1
                            self.total_bytes += entry.stat().st_size
                        elif entry.is_dir():
                            stack.append(entry.path)
            except OSError:
                pass
            
            # Update UI every 100 folders to avoid lag
            if len(stack) % 10 == 0:
                self.update_scan_ui()
                
        self.is_scanning = False
        self.update_scan_ui()
        self.root.after(0, lambda: self.lbl_status.config(text="SCAN COMPLETE"))
        self.root.after(0, lambda: self.btn_burn.config(state="normal"))

    def update_scan_ui(self):
        gb = self.total_bytes / (1024**3)
        self.root.after(0, lambda: self.card_files.config(text=f"{self.total_files:,}"))
        self.root.after(0, lambda: self.card_size.config(text=f"{gb:.2f} GB"))

    # --- DESTRUCTION ENGINE ---
    def start_burn(self):
        if not messagebox.askyesno("CONFIRM DESTRUCTION", f"Permanently delete {self.total_files} files?\nThis cannot be undone."):
            return
            
        self.is_burning = True
        self.btn_burn.config(state="disabled", text="BURNING...", bg="#550000")
        self.deleted_files = 0
        self.deleted_bytes = 0
        threading.Thread(target=self._burn_thread, daemon=True).start()

    def _burn_thread(self):
        # We walk bottom-up to delete files before folders
        for root, dirs, files in os.walk(self.target_path, topdown=False):
            for name in files:
                try:
                    full = os.path.join(root, name)
                    sz = os.path.getsize(full)
                    os.remove(full)
                    self.deleted_files += 1
                    self.deleted_bytes += sz
                except: pass
                
                if self.deleted_files % 50 == 0:
                    self.update_burn_ui()
            
            for name in dirs:
                try: os.rmdir(os.path.join(root, name))
                except: pass
        
        # Finally remove root
        try: os.rmdir(self.target_path)
        except: pass
        
        self.update_burn_ui()
        self.root.after(0, lambda: self.lbl_status.config(text="INCINERATION COMPLETE"))
        self.root.after(0, lambda: messagebox.showinfo("DONE", "All files vaporized."))
        self.root.after(0, lambda: self.root.destroy())

    def update_burn_ui(self):
        remaining = self.total_files - self.deleted_files
        pct = (self.deleted_files / self.total_files * 100) if self.total_files > 0 else 100
        
        msg = f"DELETED: {self.deleted_files:,} | REMAINING: {remaining:,}"
        self.root.after(0, lambda: self.lbl_status.config(text=msg))
        self.root.after(0, lambda: self.pb.config(value=pct))