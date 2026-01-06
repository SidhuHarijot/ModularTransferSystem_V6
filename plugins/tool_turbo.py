import subprocess
import tkinter as tk
from tkinter import messagebox
from core.interfaces import ITool

class TurboTool(ITool):
    @property
    def name(self): return "⚡ Turbo Mode (Disable AV)"
    
    def run(self, parent):
        # Simple popup to confirm
        if messagebox.askyesno("Turbo Mode", "Add exclusions to Windows Defender for C:\\ and D:\\?\n(Requires Admin)"):
            cmd = "Add-MpPreference -ExclusionPath 'C:\\', 'D:\\'"
            try:
                subprocess.run(["powershell", "-Command", cmd], shell=True)
                messagebox.showinfo("Turbo", "Exclusions Added! Speeds should increase.")
            except:
                messagebox.showerror("Error", "Failed. Run App as Administrator.")