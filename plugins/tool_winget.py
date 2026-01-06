import tkinter as tk
from tkinter import messagebox
import os
from core.interfaces import ITool

class WingetTool(ITool):
    @property
    def name(self): return "📦 Generate App Installer"
    
    def run(self, parent):
        apps = {
            "Chrome": "Google.Chrome", "Firefox": "Mozilla.Firefox", 
            "VLC": "VideoLAN.VLC", "Zoom": "Zoom.Zoom", 
            "Adobe Reader": "Adobe.Acrobat.Reader.64-bit"
        }
        lines = ["@echo off", "echo Installing Standard Apps..."]
        for k, v in apps.items():
            lines.append(f"winget install --id {v} -e --silent --accept-package-agreements --accept-source-agreements")
        lines.append("pause")
        
        path = os.path.join(os.path.expanduser("~"), "Desktop", "Install_Apps.bat")
        try:
            with open(path, "w") as f: f.write("\n".join(lines))
            messagebox.showinfo("Success", f"Saved to Desktop: {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))