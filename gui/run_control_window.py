
import tkinter as tk
from tkinter import ttk

class RunControlWindow(tk.Toplevel):
    """
    UI #2: Run Control (Pause/Resume/Abort + quick settings)
    Talks to JobManager flags + TelemetryHub (RAM).
    """
    def __init__(self, parent, job_mgr, hub):
        super().__init__(parent)
        self.title("Run Control")
        self.geometry("360x220")
        self.job_mgr = job_mgr
        self.hub = hub

        self.configure(bg="#0a0a0a")

        self.status = tk.StringVar(value="RUNNING")
        self.threads = tk.IntVar(value=int(hub.snapshot().get("active_threads") or 8))

        tk.Label(self, text="RUN CONTROL", fg="#00ff9d", bg="#0a0a0a", font=("Segoe UI", 14, "bold")).pack(pady=(12, 6))

        row = tk.Frame(self, bg="#0a0a0a")
        row.pack(pady=8)

        self.btn_pause = tk.Button(row, text="Pause", width=12, command=self.pause)
        self.btn_pause.pack(side="left", padx=6)

        self.btn_resume = tk.Button(row, text="Resume", width=12, command=self.resume)
        self.btn_resume.pack(side="left", padx=6)

        row2 = tk.Frame(self, bg="#0a0a0a")
        row2.pack(pady=8)

        tk.Label(row2, text="Threads", fg="white", bg="#0a0a0a").pack(side="left", padx=(6, 8))
        ttk.Spinbox(row2, from_=1, to=64, textvariable=self.threads, width=6, command=self.apply_threads).pack(side="left")
        tk.Button(row2, text="Apply", command=self.apply_threads).pack(side="left", padx=8)

        row3 = tk.Frame(self, bg="#0a0a0a")
        row3.pack(pady=10)
        tk.Button(row3, text="ABORT", width=28, bg="#aa2222", fg="white", command=self.abort).pack()

        tk.Label(self, textvariable=self.status, fg="#888", bg="#0a0a0a").pack(pady=(8, 0))

    def pause(self):
        try:
            self.job_mgr.pause_event.clear()
            self.job_mgr.job_data["status"] = "PAUSED"
            self.hub.update(run_status="PAUSED")
            self.status.set("PAUSED")
        except Exception:
            pass

    def resume(self):
        try:
            self.job_mgr.pause_event.set()
            self.job_mgr.job_data["status"] = "RUNNING"
            self.hub.update(run_status="RUNNING")
            self.status.set("RUNNING")
        except Exception:
            pass

    def abort(self):
        try:
            self.job_mgr.cancel_flag = True
            self.job_mgr.job_data["status"] = "ABORTING"
            self.hub.update(run_status="ABORTING")
            self.status.set("ABORTING…")
        except Exception:
            pass

    def apply_threads(self):
        # If your strategy supports reading job_mgr.history or config live, wire it here.
        # For now, we just expose it in telemetry.
        try:
            self.hub.update(active_threads=int(self.threads.get()))
        except Exception:
            pass
