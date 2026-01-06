import subprocess
import re

class NetworkConfigurator:
    @staticmethod
    def get_adapters():
        # Returns list of interface names
        try:
            res = subprocess.check_output('netsh interface ip show config', shell=True).decode('utf-8', errors='ignore')
            adapters = re.findall(r'Configuration for interface "([^"]+)"', res)
            return adapters
        except: return []

    @staticmethod
    def set_static_ip(interface, ip, subnet="255.255.255.0"):
        # USAGE: netsh interface ip set address "Ethernet" static 192.168.55.1 255.255.255.0
        cmd = f'netsh interface ip set address "{interface}" static {ip} {subnet}'
        try:
            subprocess.run(cmd, shell=True, check=True)
            return True, "IP Set Successfully"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def set_dhcp(interface):
        cmd = f'netsh interface ip set address "{interface}" source=dhcp'
        try:
            subprocess.run(cmd, shell=True, check=True)
            return True, "Reset to DHCP"
        except Exception as e:
            return False, str(e)