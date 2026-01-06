import os
import random
import time

# --- CONFIGURATION ---
TARGET_PATH = "C:/StressTest_Source"  # <--- CHANGE THIS TO YOUR SOURCE FOLDER
TOTAL_GB_TO_ADD = 9.0                     # How much data to generate
GIANT_CHANCE = 0.2                        # 20% chance of a Giant file (>500MB)
NEW_FOLDER_CHANCE = 0.3                   # 30% chance to make a new folder

# SIZES (in MB)
SIZE_MED_MIN = 50
SIZE_MED_MAX = 300
SIZE_BIG_MIN = 600  # Explicitly above your 500MB threshold
SIZE_BIG_MAX = 1500

def get_random_buffer(size_mb):
    # Create 1MB of random data to repeat (Fast & defeats zero-compression)
    return os.urandom(1024 * 1024)

def generate_chaos():
    if not os.path.exists(TARGET_PATH):
        print(f"❌ ERROR: Path '{TARGET_PATH}' does not exist.")
        return

    print(f"--- 🌪️ CHAOS GENERATOR V1 ---")
    print(f"Target: {TARGET_PATH}")
    print(f"Goal: Add {TOTAL_GB_TO_ADD} GB of Mixed Data")
    print("Scanning existing subfolders...")

    # 1. Map existing folders
    existing_folders = [TARGET_PATH]
    for root, dirs, files in os.walk(TARGET_PATH):
        for d in dirs:
            existing_folders.append(os.path.join(root, d))
    
    print(f"Found {len(existing_folders)} existing folders to pollute.")
    
    bytes_written = 0
    target_bytes = TOTAL_GB_TO_ADD * 1024 * 1024 * 1024
    files_created = 0
    
    # Pre-generate a 1MB chunk of noise (for speed)
    chunk = get_random_buffer(1) 
    
    while bytes_written < target_bytes:
        # A. Determine Size
        is_giant = random.random() < GIANT_CHANCE
        if is_giant:
            size_mb = random.randint(SIZE_BIG_MIN, SIZE_BIG_MAX)
            prefix = "GIANT"
        else:
            size_mb = random.randint(SIZE_MED_MIN, SIZE_MED_MAX)
            prefix = "MED"
            
        # B. Determine Location
        if random.random() < NEW_FOLDER_CHANCE:
            # Create new folder
            folder_name = f"Generated_Data_{random.randint(1000, 9999)}"
            target_dir = os.path.join(TARGET_PATH, folder_name)
            os.makedirs(target_dir, exist_ok=True)
            if target_dir not in existing_folders:
                existing_folders.append(target_dir)
        else:
            # Use existing folder
            target_dir = random.choice(existing_folders)
            
        # C. Generate File
        fname = f"{prefix}_{int(time.time())}_{random.randint(100,999)}.dat"
        fpath = os.path.join(target_dir, fname)
        
        print(f"[{files_created+1}] Writing {prefix} file ({size_mb} MB) to \{os.path.basename(target_dir)}... ", end="", flush=True)
        
        try:
            with open(fpath, "wb") as f:
                # Write the 1MB chunk repeatedly (Fast IO)
                for _ in range(size_mb):
                    f.write(chunk)
            
            bytes_written += size_mb * 1024 * 1024
            files_created += 1
            print("✅")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Update stats
        progress = (bytes_written / target_bytes) * 100
        print(f"   >>> Progress: {progress:.1f}% ({bytes_written/1024/1024/1024:.2f} GB)")

    print(f"\n🎉 MISSION ACCOMPLISHED.")
    print(f"Added {files_created} files totaling {bytes_written/1024/1024/1024:.2f} GB.")

if __name__ == "__main__":
    # Safety Check
    confirm = input(f"Write ~{TOTAL_GB_TO_ADD}GB to {TARGET_PATH}? (y/n): ")
    if confirm.lower() == 'y':
        generate_chaos()
    else:
        print("Aborted.")