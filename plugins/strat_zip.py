import os
import zipfile
import time
from core.interfaces import ITransferStrategy

class ZipArchiveStrategy(ITransferStrategy):
    @property
    def name(self): return "Zip Archive (Fast for small files)"

    def execute_job(self, job_mgr, src, dst, callback, config=None):
        # FIX: Use 'src'/'dst' keys
        s_root = job_mgr.job_data["src"]
        d_root = job_mgr.job_data["dst"]
        
        zip_name = "Transfer_Archive.zip"
        s_zip = os.path.join(s_root, zip_name)
        d_zip = os.path.join(d_root, zip_name)
        
        callback("GLOBAL", "init", 100)
        
        try:
            # PHASE 1
            if job_mgr.job_data.get("zip_phase", "INIT") == "INIT":
                callback("ZIP", "status", "Phase 1: Creating Zip...")
                all_files = []
                for b in job_mgr.job_data["batches"]: all_files.extend(b["files"])
                total_sz = sum(f["sz"] for f in all_files)
                current_sz = 0
                
                with zipfile.ZipFile(s_zip, 'w', zipfile.ZIP_STORED) as zf:
                    for f in all_files:
                        zf.write(f["src"], f["rel"])
                        current_sz += f["sz"]
                        callback("ZIP", "progress", (current_sz/total_sz)*100 if total_sz else 0)
                
                job_mgr.update_zip_phase("ZIPPED")
            
            # PHASE 2
            if job_mgr.job_data["zip_phase"] == "ZIPPED":
                callback("ZIP", "status", "Phase 2: Transferring Zip...")
                dst.ensure_dir(d_zip)
                sz = os.path.getsize(s_zip)
                
                with open(s_zip, 'rb') as fs, open(d_zip, 'wb') as fd:
                    copied = 0
                    last = time.time()
                    since = 0
                    while True:
                        buf = fs.read(4*1024*1024)
                        if not buf: break
                        fd.write(buf)
                        copied += len(buf)
                        since += len(buf)
                        
                        now = time.time()
                        if now - last > 0.2:
                            spd = since / (now - last)
                            callback("ZIP", "transfer_stats", {"done": copied, "total": sz, "speed": spd})
                            last = now
                            since = 0
                job_mgr.update_zip_phase("MOVED")

            # PHASE 3
            if job_mgr.job_data["zip_phase"] == "MOVED":
                callback("ZIP", "status", "Phase 3: Extracting...")
                with zipfile.ZipFile(d_zip, 'r') as zf: zf.extractall(d_root)
                job_mgr.update_zip_phase("DONE")
                
            try:
                os.remove(s_zip)
                os.remove(d_zip)
            except: pass
            
            callback("GLOBAL", "done", "Zip Job Complete")

        except Exception as e:
            callback("GLOBAL", "error", str(e))