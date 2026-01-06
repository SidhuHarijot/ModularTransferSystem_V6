import subprocess
import platform
import os

def get_drive_type(path):
    if platform.system() != "Windows":
        return "SSD"
    
    try:
        drive_letter = os.path.splitdrive(os.path.abspath(path))[0]
        # Probe WMI for Media Type
        cmd = f'Get-PhysicalDisk | Where-Object {{ (Get-Partition -DriveLetter "{drive_letter[0]}").DiskNumber -eq $_.DeviceID }} | Select-Object -ExpandProperty MediaType'
        result = subprocess.check_output(["powershell", "-Command", cmd], stderr=subprocess.STDOUT).decode().strip()
        
        if "SSD" in result.upper(): return "SSD"
        if "HDD" in result.upper(): return "HDD"
        return "USB/EXT"
    except:
        return "DISK"