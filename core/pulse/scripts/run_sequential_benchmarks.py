import subprocess
import os
import sys
import time
from datetime import datetime

def run_script(script_path):
    print(f"\n--- Launching Sub-Benchmark: {os.path.basename(script_path)} ---")
    try:
        # Use sys.executable to ensure we use the same python interpreter
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=180)
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run {script_path}: {e}")
        return False

def generate_report(results):
    report_path = "MASTER_BENCHMARK_REPORT.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(f"# NIA SOVEREIGN OS - MASTER BENCHMARK REPORT\n")
        f.write(f"Generated: {timestamp}\n\n")
        f.write(f"## 1. Modality Status Table\n")
        f.write(f"| Modality | Status | Integration | Result |\n")
        f.write(f"| :--- | :--- | :--- | :--- |\n")
        
        for name, status in results.items():
            icon = "PASS" if status else "FAIL"
            f.write(f"| {name} | Live | Direct | {icon} |\n")
            
        f.write(f"\n## 2. Integrity Verification\n")
        f.write(f"All NIA Sovereign modalities have been sequentially tested for V18 Harmonization. ")
        f.write(f"Calculated Sovereignty Score: {sum(results.values())/len(results)*100:.1f}%\n")

    print(f"\n[REPORT]: Master report generated at {report_path}")

def main():
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    base_dir = os.path.dirname(os.path.abspath(__file__))
    scripts = [
        os.path.join(base_dir, "vision_test_v18.py"),
        os.path.join(base_dir, "voice_test_v18.py"),
        os.path.join(base_dir, "mesh_test_v18.py"),
        os.path.join(base_dir, "immune_test_v18.py"),
        os.path.join(base_dir, "verify_sovereign_logic.py"),
    ]
    
    results = {}
    
    print("+" + "="*54 + "+")
    print("|        NIA SOVEREIGN V18 SEQUENTIAL BENCHMARK        |")
    print("+" + "="*54 + "+\n")
    
    for script in scripts:
        name = os.path.basename(script).replace(".py", "").replace("_", " ").title()
        if os.path.exists(script):
            success = run_script(script)
            results[name] = success
        else:
            print(f"[SKIP]: {script} not found.")
            results[name] = False
            
    generate_report(results)

if __name__ == "__main__":
    main()
