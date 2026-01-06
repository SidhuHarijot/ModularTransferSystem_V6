import socket
import os
import struct
import json

class GeekLinkClient:
    def __init__(self, ip, port=5000):
        self.ip = ip
        self.port = port
        self.sock = None

    def connect_socket(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((self.ip, self.port))
            return s
        except: return None

    def push_config(self, config_dict):
        # COMMAND: 'C' (Config)
        s = self.connect_socket()
        if not s: return False
        
        try:
            payload = json.dumps(config_dict).encode('utf-8')
            header = struct.pack(f'!cI', b'C', len(payload)) # Command + Length
            
            s.sendall(header)
            s.sendall(payload)
            
            ack = s.recv(2)
            return ack == b'OK'
        except Exception as e:
            print(f"Config Push Failed: {e}")
            return False
        finally:
            s.close()

    def send_file(self, src_path, target_abs_path, callback_progress=None):
        # COMMAND: 'F' (File)
        s = self.connect_socket()
        if not s: return False
        
        try:
            filesize = os.path.getsize(src_path)
            encoded_path = target_abs_path.encode('utf-8')
            
            # Header: Cmd(1) + PathLen(4) + Path + Size(8)
            # We use a combined struct approach
            path_len = len(encoded_path)
            # !c = char (cmd), I = int (path len), s = string, Q = long long (size)
            header = struct.pack(f'!cI{path_len}sQ', b'F', path_len, encoded_path, filesize)
            
            s.sendall(header)
            
            sent = 0
            with open(src_path, 'rb') as f:
                while True:
                    chunk = f.read(64*1024)
                    if not chunk: break
                    s.sendall(chunk)
                    sent += len(chunk)
                    if callback_progress: callback_progress(len(chunk))
            
            ack = s.recv(2)
            return ack == b'OK'
        except: return False
        finally:
            s.close()