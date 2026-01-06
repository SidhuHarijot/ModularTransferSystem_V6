import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import webbrowser
import re

from gui.ui_styles import apply_styles, BG_DARK
from gui.ui_top_bar import TopBarComponent
from gui.ui_sidebar import SidebarComponent
from gui.ui_console import ConsoleComponent
from gui.ui_mission_control import MissionControlComponent
from gui.ui_explorer import MatrixExplorer
from gui.logic_telemetry import TelemetryHandler
from gui.ui_config import ConfigWindow

from core.job_manager import JobManager
from core.plugin_loader import PluginManager
from core.transfer_config import TransferConfig

from plugins.local_fs import scan_pair_to_manifest


def disable_start(sidebar):
    try:
        sidebar.btn_start.config(state="disabled")
    except Exception:
        pass


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Modular Transfer System")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG_DARK)

        apply_styles(self.root)

        self.plugin_mgr = PluginManager()
        self.plugin_mgr.load_all()

        self.job_mgr = JobManager()
        self.t_config = TransferConfig()
        self.t_config.load()

        self.top_bar = TopBarComponent(self.root, self.open_dashboard, self.open_config)
        self.top_bar.pack(fill="x")

        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        self.dev_mode_var = tk.BooleanVar(value=False)
        self.sidebar = SidebarComponent(body, self.dev_mode_var, self.start_mission)
        self.sidebar.pack(side="left", fill="y")

        self.view_area = tk.Frame(body, bg=BG_DARK)
        self.view_area.pack(side="left", fill="both", expand=True)

        self.console = ConsoleComponent(self.root)
        self.console.pack(fill="x")

        self.telemetry = TelemetryHandler(self.job_mgr, self.plugin_mgr, self.console)

        self.pairs = []
        self.deck_tree = None
        self.mission_ui = None

        self._mode = "SETUP"
        self._paused = False

        # dynamic stream count targets
        self._stream_target = 8
        self._max_seen_target = 8

        # batch_id -> slot
        self._batch_to_slot = {}

        self.show_setup()

    def log(self, level, msg):
        try:
            self.console.log(level, msg)
        except Exception:
            print(f"[{level}] {msg}")

    # ---- Top bar ----
    def open_dashboard(self):
        # Keep as-is in your project; dashboard work is separate
        try:
            path = os.path.abspath(self.telemetry.live_html.html_path)
            webbrowser.open(f"file:///{path}")
        except Exception as e:
            messagebox.showerror("Dashboard", str(e))

    def open_config(self):
        ConfigWindow(self.root, self.t_config)

    # ---- Explorer ----
    def open_explorer(self):
        MatrixExplorer(self.root, self._add_pair_from_explorer)

    def _add_pair_from_explorer(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            for pair in args[0]:
                try:
                    src, dst = pair
                except Exception:
                    continue
                self._push_pair(src, dst)
        elif len(args) == 2:
            src, dst = args
            self._push_pair(src, dst)

    def _push_pair(self, src, dst):
        self.pairs.append((src, dst))
        if self.deck_tree is not None:
            self.deck_tree.insert("", "end", values=(src, dst))
        self.sidebar.set_ready()

    # ---- Setup view ----
    def show_setup(self):
        self._mode = "SETUP"
        for w in self.view_area.winfo_children():
            w.destroy()

        header = tk.Frame(self.view_area, bg=BG_DARK)
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(header, text="MISSION SETUP", font=("Impact", 22), bg=BG_DARK, fg="white").pack(side="left")

        btns = tk.Frame(header, bg=BG_DARK)
        btns.pack(side="right")

        tk.Button(btns, text="Add Pair", command=self.open_explorer).pack(side="left", padx=6)
        tk.Button(btns, text="Scan", command=self.run_scan).pack(side="left", padx=6)

        self.deck_tree = ttk.Treeview(self.view_area, columns=("src", "dst"), show="headings", height=18)
        self.deck_tree.heading("src", text="SOURCE")
        self.deck_tree.heading("dst", text="DESTINATION")
        self.deck_tree.pack(fill="both", expand=True, padx=20, pady=10)

        for s, d in self.pairs:
            self.deck_tree.insert("", "end", values=(s, d))

        if self.pairs:
            self.sidebar.set_ready()
        else:
            disable_start(self.sidebar)

        self._set_sidebar_mode_setup()

    def _set_sidebar_mode_setup(self):
        # If your SidebarComponent supports changing buttons, hook it here.
        # Minimal: keep Start Mission callback as start_mission.
        pass

    # ---- Scan ----
    def run_scan(self):
        if not self.pairs:
            messagebox.showwarning("No pairs", "Add at least one source/destination pair first.")
            return

        self.sidebar.set_preparing()
        self.log("SYSTEM", "SCAN STARTED…")

        try:
            self.job_mgr.create_new_job([s for s, _ in self.pairs], [d for _, d in self.pairs])
            self.job_mgr.start_clock()

            for src, dst in self.pairs:
                scan_pair_to_manifest(src, dst, self.job_mgr, self.t_config)

            self.log("SYSTEM", f"SCAN DONE. Batches: {len(self.job_mgr.job_data.get('batches', []))}")
            self.telemetry.refresh_static_data()
            self.sidebar.set_ready()

        except Exception as e:
            disable_start(self.sidebar)
            self.log("ERROR", f"Scan failed: {e}")

    # ---- Running mode ----
    def start_mission(self):
        if not self.job_mgr.job_data.get("batches"):
            messagebox.showwarning("Nothing to run", "Run Scan first so batches are created.")
            return

        self._mode = "RUNNING"
        self._paused = False
        self._batch_to_slot = {}

        # estimate initial stream count from config if present
        try:
            self._stream_target = int(self.t_config.get("starting_threads", 8))
        except Exception:
            self._stream_target = 8
        self._max_seen_target = self._stream_target

        for w in self.view_area.winfo_children():
            w.destroy()

        self.mission_ui = MissionControlComponent(self.view_area, self.job_mgr)
        self.mission_ui.pack(fill="both", expand=True)

        # Dynamic: create exactly the target number of stream widgets
        self.mission_ui.set_slot_count(self._stream_target)

        self.log("SYSTEM", "MISSION STARTED…")

        strat = None
        for s in getattr(self.plugin_mgr, "strategies", []):
            if getattr(s, "name", "") == "Standard":
                strat = s
                break
        if strat is None and getattr(self.plugin_mgr, "strategies", []):
            strat = self.plugin_mgr.strategies[0]

        if strat is None:
            self.log("ERROR", "No transfer strategy found.")
            return

        t = threading.Thread(
            target=lambda: strat.execute_job(self.job_mgr, None, None, self.engine_callback, self.t_config),
            daemon=True
        )
        t.start()

        self._set_sidebar_mode_running()

    def _set_sidebar_mode_running(self):
        # If SidebarComponent has a footer area, you should replace it with:
        # - Pause/Resume button
        # - Abort button
        # Since we don't know SidebarComponent internals here, we keep logic ready:
        pass

    def engine_callback(self, bid, evt, data):
        self.root.after(0, self._process_callback, bid, evt, data)

    def _parse_target_threads(self, msg: str):
        # tuner message format: "... [12]"
        m = re.search(r"\[(\d+)\]", str(msg))
        if not m:
            return None
        try:
            return int(m.group(1))
        except Exception:
            return None

    def _process_callback(self, bid, evt, data):
        if not self.mission_ui:
            return

        # GLOBAL: tuner target updates -> resize stream widgets
        if bid == "GLOBAL" and evt == "tuner":
            n = self._parse_target_threads(data)
            if n:
                self._max_seen_target = max(self._max_seen_target, n)
                # cap to 32 to avoid insane UI
                n = max(1, min(32, n))
                if n != self._stream_target:
                    self._stream_target = n
                    self.mission_ui.set_slot_count(self._stream_target)
            return

        # Batch start: data has {"count": files_total, "size": bytes_total}
        if evt == "start":
            files_total = int((data or {}).get("count", 0) or 0)
            bytes_total = int((data or {}).get("size", 0) or 0)

            # assign to a free slot
            slot = self.mission_ui.first_free_slot()
            if slot is None:
                # if no free slot, grow up to max_seen_target+1 (safe)
                if len(self.mission_ui.slots) < 32:
                    self.mission_ui.set_slot_count(len(self.mission_ui.slots) + 1)
                    slot = self.mission_ui.first_free_slot()

            if slot:
                slot.assign(bid, files_total, bytes_total)
                self._batch_to_slot[bid] = slot
            return

        if evt == "file":
            slot = self._batch_to_slot.get(bid)
            if slot:
                slot.on_file()
            return

        if evt == "progress":
            slot = self._batch_to_slot.get(bid)
            if slot:
                bytes_done = int((data or {}).get("bytes", 0) or 0)
                slot.update_bytes(bytes_done)
            return

        if evt == "done":
            slot = self._batch_to_slot.pop(bid, None)
            if slot:
                slot.done()
            return
