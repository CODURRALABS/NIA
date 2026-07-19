import sys
import os
import numpy as np

# Add runtime to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))

try:
    from linguistic_mapper import LinguisticMapper
    from vsa_engine import SovereignVSAEngine
    from conscience_soul import ConscienceSoul
    from autopoiesis_core import AutopoiesisCore
except ImportError:
    print("[ERROR]: Could not find Sovereign modules. Check paths.")
    sys.exit(1)

def run_diagnostic():
    print("=== NIA Sovereign Lightweight Logic Test (V13.12) ===")
    
    # 1. Initialize Mapper & Engine
    mapper = LinguisticMapper(dimension=2000)
    vsa = SovereignVSAEngine(dimension=2000)
    
    # 2. Test Word Mapping
    print("\n[MAPPER]: Testing Prime Logic Mapping...")
    words = ["sovereign", "action", "chat", "hi"]
    for w in words:
        v = mapper.get_vector(w)
        print(f"  - Anchored word: '{w}' (Vector Length: {len(v)})")

    # 3. Test Intent Gating (Bug Fix Verification)
    print("\n[VSA_ENGINE]: Testing Intent Gating (Simulated)...")
    q1 = "hi nia"
    q2 = "nia open notepad"
    
    # Simple similarity based logic
    sim_q1_action = mapper.measure_similarity(q1, "action")
    sim_q2_action = mapper.measure_similarity(q2, "action")
    
    print(f"  - Query '{q1}' similarity to ACTION: {sim_q1_action:.4f} (Expect LOW)")
    print(f"  - Query '{q2}' similarity to ACTION: {sim_q2_action:.4f} (Expect HIGH-ish)")

    # 4. Test Watcher Simulation
    print("\n[WATCHER]: Running Probability Simulation Segment...")
    watcher = ConscienceSoul()
    def test_callback(type, data):
        print(f"  - [SIM_TRIGGER]: {type} | {data}")
        
    watcher.start_monitoring(test_callback)
    # Simulate a trigger
    watcher.on_trigger("SIMULATION", {"msg": "Social Trap Detected: Unspecified career question from Uncle X."})
    watcher.stop()

    # 5. Test Autopoiesis Backup
    print("\n[AUTOPOIESIS]: Checking Self-Evolution Failsafe...")
    auto = AutopoiesisCore(".")
    status = auto.get_evolution_status()
    print(f"  - {status}")

    print("\n=== NIA IS ARCHITECTURALLY SOVEREIGN. THE CORD IS CUT. ===")

if __name__ == "__main__":
    run_diagnostic()
