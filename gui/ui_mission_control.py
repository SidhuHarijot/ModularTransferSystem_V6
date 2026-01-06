import tkinter as tk

from .ui_styles import BG_DARK, ACCENT
from .ui_widgets import StreamWidget
from .scroll_frame import ScrollableFrame

class MissionControlComponent(tk.Frame):
    def __init__(self, parent, job_mgr):
        super().__init__(parent, bg=BG_DARK)
        self.jm = job_mgr
        self.slots = []

        f_strm = tk.LabelFrame(
            self,
            text=" STREAMS ",
            bg=BG_DARK,
            fg=ACCENT,
            font=("Consolas", 10, "bold"),
            bd=1,
            relief="solid"
        )
        f_strm.pack(fill="both", expand=True, padx=16, pady=12)

        self.scroll = ScrollableFrame(f_strm)
        self.scroll.pack(fill="both", expand=True)

    def set_slot_count(self, n: int):
        n = max(1, min(32, int(n or 1)))

        # create more
        while len(self.slots) < n:
            slot = StreamWidget(self.scroll.scrollable_frame, len(self.slots))
            slot.pack(fill="x", padx=10, pady=6)
            self.slots.append(slot)

        # remove extra
        while len(self.slots) > n:
            slot = self.slots.pop()
            slot.destroy()

    def first_free_slot(self):
        for slot in self.slots:
            if slot.curr_batch_id is None:
                return slot
        return None
