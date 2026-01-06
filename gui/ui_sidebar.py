import tkinter as tk
from gui.ui_styles import BG_PANEL, ACCENT

class SidebarComponent(tk.Frame):
    def __init__(self, parent, dev_mode_var, start_callback):
        super().__init__(parent, bg=BG_PANEL, width=320, bd=1, relief="solid")
        self.pack_propagate(False)
        self.dev_mode = dev_mode_var
        self.start_callback = start_callback
        
        tk.Label(self, text="COMMAND SIDEBAR", font=("Impact", 18), bg="#222", fg=ACCENT).pack(fill="x", pady=(0, 10))
        
        # 1. MANUAL OVERRIDE
        f_ovr = tk.Frame(self, bg="#331133", pady=5)
        f_ovr.pack(fill="x", padx=10, pady=5)
        tk.Checkbutton(f_ovr, text="MANUAL OVERRIDE (MAX)", variable=self.dev_mode, 
                       bg="#331133", fg="#ff00ff", selectcolor="#000", font=("Consolas", 10, "bold")).pack()

        self.mk_sec("FILTERS", [("Ignore Temp Files", True), ("Ignore AppData", False)])
        self.mk_sec("CHECKS", [("Verify Size", True), ("Verify Hash", False)])
        
        # 4. ADDITIONAL FEATURES (RESTORED)
        f_feat = tk.LabelFrame(self, text=" ADDITIONAL FEATURES ", bg=BG_PANEL, fg=ACCENT, font=("Consolas", 9, "bold"))
        f_feat.pack(fill="x", padx=10, pady=5)
        tk.Button(f_feat, text="GENERATE APP LIST", bg="#333", fg="white", font=("Segoe UI", 8)).pack(fill="x", padx=5, pady=2)

        self.mk_sec("PRE-FLIGHT", [("Prevent Sleep", True), ("Admin Check", True)])

        # 6. TRANSFER SETTINGS (RESTORED)
        f_trans = tk.LabelFrame(self, text=" TRANSFER SETTINGS ", bg=BG_PANEL, fg="gray", font=("Consolas", 9, "bold"))
        f_trans.pack(fill="x", padx=10, pady=10)
        self.conflict_var = tk.IntVar(value=1)
        tk.Radiobutton(f_trans, text="Overwrite Existing", variable=self.conflict_var, value=1, 
                       bg=BG_PANEL, fg="white", selectcolor="#000").pack(anchor="w", padx=5)
        tk.Radiobutton(f_trans, text="Keep Old (.old)", variable=self.conflict_var, value=2, 
                       bg=BG_PANEL, fg="white", selectcolor="#000").pack(anchor="w", padx=5)

        # LAUNCH CONTROL
        self.btn_start = tk.Button(self, text="START MISSION", bg="#444", fg="gray", font=("Impact", 20), 
                                   state="disabled", command=self.start_callback)
        self.btn_start.pack(side="bottom", fill="x", padx=15, pady=20)

    def set_ready(self):
        self.btn_start.config(text="START MISSION", bg=ACCENT, fg="black", state="normal")

    def set_preparing(self):
        self.btn_start.config(text="PREPARING...", state="disabled", bg="#ffaa00", fg="black")

    def mk_sec(self, title, options):
        f = tk.LabelFrame(self, text=f" {title} ", bg=BG_PANEL, fg=ACCENT, font=("Consolas", 9, "bold"))
        f.pack(fill="x", padx=10, pady=5)
        for text, default_val in options:
            var = tk.BooleanVar(value=default_val)
            tk.Checkbutton(f, text=text, variable=var, bg=BG_PANEL, fg="white", 
                           selectcolor="#000", activebackground=BG_PANEL).pack(anchor="w", padx=5)