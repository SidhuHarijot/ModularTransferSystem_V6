import os
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor
from core.interfaces import ITool

# COLORS (Matching Main UI)
BG_DARK = "#121212"
BG_PANEL = "#1E1E1E"
ACCENT = "#FF3939" # Red for Danger
TEXT_MAIN = "#FFFFFF"

class FastDeleteTool(ITool):
    @property
    def name(self): return "🗑 MASS DELETE (INCINERATOR)"

    def run(self, parent):
        DeleteWindow(parent)

class DeleteWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("INCINERATOR // MASS DELETE")
        self.geometry("600x450")
        self.configure(bg=BG_DARK)
        
        self.target_dir = tk.StringVar()
        self.is_running = False
        self.cancel_flag = False
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        tk.Label(self, text="⚠ WARNING: IRREVERSIBLE DATA DESTRUCTION ⚠", fg=ACCENT, bg=BG_DARK, font=("Impact", 14)).pack(pady=15)
        
        # Path Selection
        f_path = tk.LabelFrame(self, text=" TARGET FOLDER ", bg=BG_DARK, fg="white", bd=1)
        f_path.pack(fill="x", padx=20, pady=5)
        
        e_path = tk.Entry(f_path, textvariable=self.target_dir, bg="#222222", fg="white", relief="flat")
        e_path.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        btn_browse = tk.Button(f_path, text="BROWSE", bg="#333", fg="white", command=self.browse, relief="flat")
        btn_browse.pack(side="right", padx=5, pady=5)

        # Config
        f_cfg = tk.LabelFrame(self, text=" DESTRUCTION PARAMETERS ", bg=BG_DARK, fg="white", bd=1)
        f_cfg.pack(fill="x", padx=20, pady=10)
        
        tk.Label(f_cfg, text="THREADS (SPEED):", bg=BG_DARK, fg="white").pack(anchor="w", padx=10, pady=2)
        self.stream_scale = tk.Scale(f_cfg, from_=1, to=64, orient="horizontal", bg=BG_DARK, fg=ACCENT, highlightthickness=0)
        self.stream_scale.set(16) # Default to high threads for delete
        self.stream_scale.pack(fill="x", padx=10, pady=5)
        
        # Progress
        self.lbl_status = tk.Label(self, text="READY", fg="gray", bg=BG_DARK, font=("Consolas", 10))
        self.lbl_status.pack(pady=5)
        
        self.pb = ttk.Progressbar(self, mode="determinate")
        self.pb.pack(fill="x", padx=20, pady=5)
        
        # Buttons
        f_btn = tk.Frame(self, bg=BG_DARK)
        f_btn.pack(fill="x", padx=20, pady=20)
        
        self.btn_nuke = tk.Button(f_btn, text="☢ INCINERATE", bg="#550000", fg="white", font=("Segoe UI", 12, "bold"), command=self.start_nuke)
        self.btn_nuke.pack(side="left", fill="x", expand=True, padx=5)
        
        self.btn_stop = tk.Button(f_btn, text="STOP", bg="#333", fg="white", command=self.stop, state="disabled")
        self.btn_stop.pack(side="right", fill="x", expand=True, padx=5)

    def browse(self):
        p = filedialog.askdirectory()
        if p: self.target_dir.set(p)

    def stop(self):
        self.cancel_flag = True
        self.lbl_status.config(text="STOPPING...")

    def start_nuke(self):
        path = self.target_dir.get()
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Invalid Path")
            return
            
        if not messagebox.askyesno("CONFIRM DELETION", f"Are you sure you want to permanently delete:\n{path}\n\nThis cannot be undone."):
            return

        self.is_running = True
        self.cancel_flag = False
        self.btn_nuke.config(state="disabled")
        self.btn_stop.config(state="normal")
        
        threading.Thread(target=self._nuke_thread, args=(path,), daemon=True).start()

    def _nuke_thread(self, path):
        # PHASE 1: SCANNING (Single Threaded - Fast)
        self.update_status("SCANNING FILE STRUCTURE...")
        all_files = []
        all_dirs = []
        
        try:
            for root, dirs, files in os.walk(path):
                if self.cancel_flag: break
                for f in files: all_files.append(os.path.join(root, f))
                for d in dirs: all_dirs.append(os.path.join(root, d))
        except Exception as e:
            self.update_status(f"SCAN ERROR: {e}")
            self.reset_ui()
            return

        total_items = len(all_files)
        self.update_status(f"FOUND {total_items} FILES. INITIATING DELETE...")
        
        # PHASE 2: PARALLEL FILE DELETION
        workers = self.stream_scale.get()
        deleted_count = 0
        
        def delete_file(fp):
            try:
                os.remove(fp)
                return 1
            except: return 0

        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(delete_file, f) for f in all_files]
            
            for f in futures:
                if self.cancel_flag: break
                res = f.result()
                deleted_count += res
                
                # UI Update every 100 items (to save CPU)
                if deleted_count % 100 == 0:
                    self.update_progress(deleted_count, total_items)
        
        # PHASE 3: DIRECTORY CLEANUP (Reverse Order)
        if not self.cancel_flag:
            self.update_status("REMOVING EMPTY FOLDERS...")
            # Sort by length desc so we delete sub-folders first
            all_dirs.sort(key=len, reverse=True)
            for d in all_dirs:
                try: os.rmdir(d)
                except: pass
            
            # Try to remove root
            try: os.rmdir(path)
            except: pass

            self.update_status("DELETION COMPLETE.")
            messagebox.showinfo("Done", f"Deleted {deleted_count} files.")
        else:
            self.update_status("CANCELLED.")

        self.reset_ui()

    def update_status(self, text):
        self.after(0, lambda: self.lbl_status.config(text=str(text)))

    def update_progress(self, current, total):
        pct = (current / total) * 100 if total > 0 else 0
        self.after(0, lambda: self.pb.configure(value=pct))

    def reset_ui(self):
        self.after(0, lambda: self._reset_buttons())

    def _reset_buttons(self):
        self.btn_nuke.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.pb['value'] = 0