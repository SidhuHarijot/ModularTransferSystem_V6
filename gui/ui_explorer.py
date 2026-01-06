import tkinter as tk
from tkinter import ttk
import os
import platform

class MatrixExplorer(tk.Toplevel):
    def __init__(self, parent, on_confirm_callback):
        super().__init__(parent)
        self.title("MATRIX TREE EXPLORER")
        self.geometry("1000x750")
        self.configure(bg="#050505")
        self.attributes("-topmost", True) # KEEP ON TOP
        self.callback = on_confirm_callback
        self.pairs = []
        self.setup_ui()

    def setup_ui(self):
        f_main = tk.Frame(self, bg="#050505")
        f_main.pack(fill="both", expand=True, padx=10, pady=5)
        f_main.columnconfigure(0, weight=1); f_main.columnconfigure(1, weight=1); f_main.rowconfigure(0, weight=1)

        self.tree_l = self.mk_tree_pane(f_main, "SOURCE", 0)
        self.tree_r = self.mk_tree_pane(f_main, "DESTINATION", 1)

        f_bot = tk.Frame(self, bg="#111", height=70)
        f_bot.pack(fill="x", side="bottom")
        f_bot.pack_propagate(False)
        
        # Action Buttons
        self.btn_add = tk.Button(f_bot, text="[ + ADD PAIR ]", bg="#444", fg="white", font=("Impact", 14), 
                                 command=self.add_pair, width=20)
        self.btn_add.pack(side="left", padx=20, pady=10)
        
        tk.Button(f_bot, text="[ CONFIRM & CLOSE ]", bg="#00ff9d", fg="black", font=("Impact", 14), 
                  command=self.confirm, width=20).pack(side="right", padx=20, pady=10)

    def mk_tree_pane(self, parent, title, col):
        f = tk.Frame(parent, bg="#111", bd=2, relief="flat")
        f.grid(row=0, column=col, sticky="nsew", padx=5)
        tk.Label(f, text=title, bg="#222", fg="#00ff9d", font=("Impact", 11)).pack(fill="x")
        tree = ttk.Treeview(f, show="tree", selectmode="browse")
        tree.column("#0", width=400, minwidth=200, stretch=True)
        tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(f, orient="vertical", command=tree.yview)
        sb.pack(side="right", fill="y"); tree.configure(yscrollcommand=sb.set)
        self.populate_roots(tree)
        tree.bind("<<TreeviewOpen>>", self.on_expand)
        return tree

    def populate_roots(self, tree):
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            path = f"{letter}:\\"
            if os.path.exists(path):
                node = tree.insert("", "end", text=f" DRIVE ({letter}:)", values=[path], open=False)
                tree.insert(node, "end", text="_dummy")

    def on_expand(self, event):
        tree = event.widget
        node = tree.focus()
        path = tree.item(node, "values")[0]
        for child in tree.get_children(node):
            if tree.item(child, "text") == "_dummy": tree.delete(child)
        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                prefix = "📂 " if entry.is_dir() else "📄 "
                child = tree.insert(node, "end", text=f"{prefix}{entry.name}", values=[entry.path], open=False)
                if entry.is_dir(): tree.insert(child, "end", text="_dummy")
        except: pass

    def add_pair(self):
        s_sel = self.tree_l.selection(); d_sel = self.tree_r.selection()
        if s_sel and d_sel:
            s = self.tree_l.item(s_sel[0], "values")[0]
            d = self.tree_r.item(d_sel[0], "values")[0]
            self.pairs.append((s, d))
            # Visual Feedback instead of popup
            self.btn_add.config(text=f"ADDED ({len(self.pairs)})", bg="#005500")
            self.after(500, lambda: self.btn_add.config(text="[ + ADD PAIR ]", bg="#444"))

    def confirm(self):
        if self.pairs: self.callback(self.pairs); self.destroy()