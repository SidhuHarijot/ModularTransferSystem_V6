import tkinter as tk
import time

from .ui_styles import BG_DARK, ACCENT

def _fmt_bytes(n: float) -> str:
    n = float(n or 0)
    units = ["B","KB","MB","GB","TB"]
    i = 0
    while n >= 1024 and i < len(units)-1:
        n /= 1024.0
        i += 1
    return f"{n:.0f} {units[i]}" if i == 0 else f"{n:.2f} {units[i]}"

class StreamWidget(tk.Frame):
    """
    Thin, full-width stream card with per-stream metrics.
    """
    def __init__(self, parent, stream_index: int):
        super().__init__(parent, bg="#0a0a0a", highlightthickness=1, highlightbackground="#1b1b1b")
        self.stream_index = stream_index

        self.curr_batch_id = None
        self.bytes_total = 0
        self.bytes_done = 0
        self.files_total = 0
        self.files_done = 0

        self._last_bytes = 0
        self._last_t = time.time()
        self._mb_s = 0.0

        # Layout: left info + right stats
        top = tk.Frame(self, bg="#0a0a0a")
        top.pack(fill="x", padx=10, pady=(8, 6))

        self.lbl_left = tk.Label(top, text=f"STREAM {stream_index+1:02d}", fg=ACCENT, bg="#0a0a0a",
                                 font=("Segoe UI", 10, "bold"))
        self.lbl_left.pack(side="left")

        self.lbl_batch = tk.Label(top, text="IDLE", fg="#cfcfcf", bg="#0a0a0a", font=("Segoe UI", 10))
        self.lbl_batch.pack(side="left", padx=10)

        self.lbl_speed = tk.Label(top, text="0.00 MB/s", fg="#cfcfcf", bg="#0a0a0a", font=("Segoe UI", 10))
        self.lbl_speed.pack(side="right")

        mid = tk.Frame(self, bg="#0a0a0a")
        mid.pack(fill="x", padx=10, pady=(0, 6))

        self.lbl_files = tk.Label(mid, text="Files: 0/0", fg="#8a8a8a", bg="#0a0a0a", font=("Segoe UI", 9))
        self.lbl_files.pack(side="left")

        self.lbl_bytes = tk.Label(mid, text="Bytes: 0/0", fg="#8a8a8a", bg="#0a0a0a", font=("Segoe UI", 9))
        self.lbl_bytes.pack(side="right")

        # Progress bar (thin + glow)
        bar_wrap = tk.Frame(self, bg="#0a0a0a")
        bar_wrap.pack(fill="x", padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(bar_wrap, height=10, bg="#050505", highlightthickness=1,
                                highlightbackground="#1b1b1b")
        self.canvas.pack(fill="x")

        self._bar = None
        self._bar_glow = None

        self.set_idle()

    def set_idle(self):
        self.curr_batch_id = None
        self.bytes_total = 0
        self.bytes_done = 0
        self.files_total = 0
        self.files_done = 0
        self._last_bytes = 0
        self._last_t = time.time()
        self._mb_s = 0.0

        self.lbl_batch.config(text="IDLE", fg="#666")
        self.lbl_speed.config(text="0.00 MB/s", fg="#666")
        self.lbl_files.config(text="Files: 0/0")
        self.lbl_bytes.config(text="Bytes: 0/0")
        self._draw_pct(0.0, active=False)

    def assign(self, batch_id: str, files_total: int, bytes_total: int):
        self.curr_batch_id = batch_id
        self.files_total = int(files_total or 0)
        self.bytes_total = int(bytes_total or 0)
        self.files_done = 0
        self.bytes_done = 0
        self._last_bytes = 0
        self._last_t = time.time()
        self._mb_s = 0.0

        self.lbl_batch.config(text=f"{batch_id}", fg="#eaeaea")
        self.lbl_speed.config(text="0.00 MB/s", fg="#eaeaea")
        self.lbl_files.config(text=f"Files: 0/{self.files_total}")
        self.lbl_bytes.config(text=f"Bytes: {_fmt_bytes(0)}/{_fmt_bytes(self.bytes_total)}")
        self._draw_pct(0.0, active=True)

    def on_file(self):
        if self.curr_batch_id is None:
            return
        self.files_done = min(self.files_total, self.files_done + 1)
        self.lbl_files.config(text=f"Files: {self.files_done}/{self.files_total}")

    def update_bytes(self, bytes_done: int):
        if self.curr_batch_id is None:
            return

        self.bytes_done = int(bytes_done or 0)

        # MB/s based on delta bytes over time
        now = time.time()
        dt = max(0.001, now - self._last_t)
        db = max(0, self.bytes_done - self._last_bytes)
        inst = (db / 1048576.0) / dt
        # smooth
        self._mb_s = (self._mb_s * 0.75) + (inst * 0.25)

        self._last_t = now
        self._last_bytes = self.bytes_done

        self.lbl_speed.config(text=f"{self._mb_s:.2f} MB/s", fg="#eaeaea")
        self.lbl_bytes.config(text=f"Bytes: {_fmt_bytes(self.bytes_done)}/{_fmt_bytes(self.bytes_total)}")

        pct = (self.bytes_done / self.bytes_total * 100.0) if self.bytes_total > 0 else 0.0
        self._draw_pct(pct, active=True)

    def done(self):
        self._draw_pct(100.0, active=False)
        self.set_idle()

    def _draw_pct(self, pct: float, active: bool):
        w = max(10, self.canvas.winfo_width())
        h = 10
        self.canvas.delete("all")
        fill_w = int(w * (max(0.0, min(100.0, pct)) / 100.0))
        if active:
            # glow behind
            self.canvas.create_rectangle(0, 0, fill_w, h, fill="#00ff9d", outline="")
        else:
            self.canvas.create_rectangle(0, 0, fill_w, h, fill="#3a3a3a", outline="")
