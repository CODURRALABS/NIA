import os
import sys

print(f"CWD: {os.getcwd()}")
print(f"__file__: {__file__}")
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Parent Dir (Project Root): {parent_dir}")

sys.path.append(parent_dir)
print(f"Updated sys.path: {sys.path[:3]}... (omitted)")

try:
    from src.model import NIAConfig
    print("SUCCESS: src.model import worked.")
except Exception as e:
    print(f"FAILURE: {e}")
    # Try importing directly if 'src' was already in path
    try:
        from model import NIAConfig
        print("SUCCESS: model import worked (without 'src' prefix).")
    except:
        print("FAILURE: direct model import also failed.")
