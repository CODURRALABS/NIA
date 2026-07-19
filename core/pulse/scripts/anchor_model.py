import os
import shutil
import pathlib

def anchor_nia_core():
    # 1. Define Paths
    # Current detected cache for Qwen2-0.5B-Instruct
    cache_base = r"C:\Users\Admin\.cache\huggingface\hub\models--Qwen--Qwen2-0.5B-Instruct\snapshots"
    
    if not os.path.exists(cache_base):
        print(f"[ANCHOR]: Cache base not found at {cache_base}")
        return

    # Find the snapshot folder (usually a hash)
    snapshots = os.listdir(cache_base)
    if not snapshots:
        print("[ANCHOR]: No snapshots found in cache.")
        return
    
    source_dir = os.path.join(cache_base, snapshots[0])
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "nia-core"))

    print(f"[ANCHOR]: Sourcing weights from {source_dir}")
    print(f"[ANCHOR]: Anchoring to {target_dir}")

    # 2. Create Target Directory
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    # 3. Copy Files (Sovereignty Check)
    # We copy rather than symlink to ensure NIA is independent of the HF cache system.
    try:
        files_to_copy = os.listdir(source_dir)
        for item in files_to_copy:
            s = os.path.join(source_dir, item)
            d = os.path.join(target_dir, item)
            if os.path.isdir(s):
                if not os.path.exists(d):
                    shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        print("[ANCHOR]: Sovereignty Achieved. NIA Model exported to local storage.")
    except Exception as e:
        print(f"[ANCHOR]: Export failed: {e}")

if __name__ == "__main__":
    anchor_nia_core()
