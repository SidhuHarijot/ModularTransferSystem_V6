import tkinter as tk
from tkinter import ttk, filedialog
import socket
import threading
import struct
import os
import json
from core.net_utils import NetworkConfigurator

class GeekLinkReceiver:
    def __init__(self):
        self.name = "📡 GEEK LINK RECEIVER"
        self.running = False
        self.server_sock = None
        self.save_dir = "C:/GeekLink_Data"
        self.root_win = None
        
        # UI Variables (Remote Controlled)
        self.var_verify = None
        self.var_temp = None
        self.var_app = None

    def run(self, root_window):
        self.root_win = tk.Toplevel(root_window)
        self.root_win.title("GEEK LINK RECEIVER [V3 - SLAVE MODE]")
        self.root_win.geometry("600x600")
        self.root_win.configure(bg="#111")
        
        tk.Label(self.root_win, text="RECEIVER NODE", font=("Impact", 20), bg="#111", fg="#00ff00").pack(pady=10)
        
        # IP Config
        f_net = tk.LabelFrame(self.root_win, text=" NETWORK ", bg="#111", fg="gray")
        f_net.pack(fill="x", padx=10)
        self.cb_adapter = ttk.Combobox(f_net, values=NetworkConfigurator.get_adapters())
        self.cb_adapter.pack(side="left", padx=5, fill="x", expand=True)
        if self.cb_adapter['values']: self.cb_adapter.current(0)
        tk.Button(f_net, text="SET IP .2", bg="#004444", fg="white", command=lambda: self.set_ip("192.168.55.2")).pack(side="left", padx=5)

        # Settings (Read Only / Remote Controlled)
        f_sets = tk.LabelFrame(self.root_win, text=" ACTIVE SETTINGS (CONTROLLED BY SENDER) ", bg="#111", fg="#00ccff")
        f_sets.pack(fill="x", padx=10, pady=10)
        
        self.var_verify = tk.BooleanVar(value=False)
        self.var_temp = tk.BooleanVar(value=True)
        self.var_app = tk.BooleanVar(value=False)
        
        # Disabled state indicates they are managed remotely, but we let user toggle if disconnected
        tk.Checkbutton(f_sets, text="Verify Hash", variable=self.var_verify, bg="#111", fg="white", selectcolor="#333").pack(anchor="w", padx=10)
        tk.Checkbutton(f_sets, text="Skip Temp", variable=self.var_temp, bg="#111", fg="white", selectcolor="#333").pack(anchor="w", padx=10)
        tk.Checkbutton(f_sets, text="Skip AppData", variable=self.var_app, bg="#111", fg="white", selectcolor="#333").pack(anchor="w", padx=10)

        # File Browser
        f_path = tk.Frame(self.root_win, bg="#111")
        f_path.pack(fill="x", padx=10, pady=5)
        tk.Label(f_path, text="DEFAULT SAVE ROOT:", bg="#111", fg="gray").pack(anchor="w")
        self.lbl_path = tk.Label(f_path, text=self.save_dir, bg="#222", fg="#0f0", relief="sunken", anchor="w")
        self.lbl_path.pack(fill="x")
        tk.Button(f_path, text="CHANGE ROOT", bg="#333", fg="white", command=self.browse_root).pack(anchor="e", pady=2)

        # Logs
        self.btn_listen = tk.Button(self.root_win, text="START LISTENING", bg="#005500", fg="white", font=("Consolas", 14), command=self.toggle_server)
        self.btn_listen.pack(fill="x", padx=20, pady=10)
        
        self.log_box = tk.Text(self.root_win, bg="black", fg="#00ff00", height=10, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def set_ip(self, ip):
        adap = self.cb_adapter.get()
        if adap: NetworkConfigurator.set_static_ip(adap, ip)

    def browse_root(self):
        p = filedialog.askdirectory()
        if p:
            self.save_dir = p
            self.lbl_path.config(text=p)

    def log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, f">> {msg}\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    def toggle_server(self):
        if not self.running:
            self.running = True
            self.btn_listen.config(text="STOP LISTENING", bg="#550000")
            threading.Thread(target=self.server_loop, daemon=True).start()
        else:
            self.running = False
            if self.server_sock: self.server_sock.close()
            self.btn_listen.config(text="START LISTENING", bg="#005500")

    def server_loop(self):
        self.log("Listening on Port 5000...")
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.bind(('0.0.0.0', 5000))
            self.server_sock.listen(5)
            
            while self.running:
                try:
                    client, addr = self.server_sock.accept()
                    # Handle sequentially to avoid race conditions on settings update
                    self.handle_client(client) 
                except: break
        except Exception as e: self.log(f"Server Error: {e}")

    def handle_client(self, conn):
        try:
            # READ COMMAND (1 Byte)
            cmd = conn.recv(1)
            
            if cmd == b'C': # CONFIG PUSH
                self.handle_config(conn)
            elif cmd == b'F': # FILE TRANSFER
                self.handle_file(conn)
                
        except Exception as e:
            self.log(f"Client Err: {e}")
        finally:
            conn.close()

    def handle_config(self, conn):
        # 1. Read Length (4 bytes)
        raw_len = self.recv_all(conn, 4)
        if not raw_len: return
        length = struct.unpack('!I', raw_len)[0]
        
        # 2. Read JSON
        data = self.recv_all(conn, length)
        config = json.loads(data.decode('utf-8'))
        
        # 3. Apply to UI (Thread safe-ish for Tkinter variables)
        self.log("Received Settings Update from Master.")
        if 'skip_temp' in config: self.var_temp.set(config['skip_temp'])
        if 'skip_appdata' in config: self.var_app.set(config['skip_appdata'])
        if 'verify' in config: self.var_verify.set(config['verify'])
        
        conn.sendall(b'OK')

    def handle_file(self, conn):
        # 1. Path Len
        raw_len = self.recv_all(conn, 4)
        if not raw_len: return
        path_len = struct.unpack('!I', raw_len)[0]
        
        # 2. Path
        path_bytes = self.recv_all(conn, path_len)
        rel_path = path_bytes.decode('utf-8')
        
        # 3. Size
        raw_size = self.recv_all(conn, 8)
        file_size = struct.unpack('!Q', raw_size)[0]
        
        # 4. Determine Save Path
        # If absolute path provided (e.g. D:/...), try to use it if drive exists
        # Else, map to save_dir
        if os.path.isabs(rel_path) and os.path.exists(os.path.splitdrive(rel_path)[0]):
            dest_path = rel_path
        else:
            # Strip drive letter if present to append to root
            clean_rel = os.path.splitdrive(rel_path)[1] 
            if clean_rel.startswith(os.sep): clean_rel = clean_rel[1:]
            dest_path = os.path.join(self.save_dir, clean_rel)
            
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # 5. Receive Data
        received = 0
        with open(dest_path, 'wb') as f:
            while received < file_size:
                chunk = conn.recv(min(64*1024, file_size - received))
                if not chunk: break
                f.write(chunk)
                received += len(chunk)
        
        conn.sendall(b'OK')

    def recv_all(self, sock, n):
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet: return None
            data += packet
        return data