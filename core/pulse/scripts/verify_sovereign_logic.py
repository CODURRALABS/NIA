import asyncio
import os
import sys

# Add runtime to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))

try:
    from chat import NIASovereignCore
except ImportError:
    # Workaround for varied environments
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runtime")))
    from chat import NIASovereignCore

async def verify_NIA_logic():
    print("=== NIA Sovereign Logic Verification (V13.6) ===")
    
    # Initialize Core (Force CPU for verification if needed, but here we just test logic)
    engine = NIASovereignCore(device="cpu")
    
    # 1. Test Recursive Reasoning (Logical Symmetry)
    print("\n[TEST 1]: Recursive Reasoning Paradox Test")
    user_query = "If a robot says 'I am lying', is it telling the truth? Think recursively."
    # We want to see [RECURSION] logs in console
    response = await engine.process_task(user_query)
    print(f"Response: {response}")
    
    # 2. Test Hardware Logic (Trivial Risk)
    print("\n[TEST 2]: Hardware Integration (Volume)")
    # Should execute without confirmation
    await engine.process_task("Nia, set volume to 10 percent")
    print("Volume check complete.")

    # 3. Test Proactive Intervention (Conscience)
    print("\n[TEST 3]: Proactive Conscience Trigger")
    # Manually trigger the intervention handler
    await engine.handle_proactive_trigger("DISTRACTION", {"app": "Netflix", "duration": 7200}) # 2 hours
    print("Notification and Voice trigger sent.")
    
    # 4. Test Risk Classifier
    print("\n[TEST 4]: Risk Tiering")
    critical_risk = engine.classify_risk("Shut down my computer")
    trivial_risk = engine.classify_risk("Increase brightness")
    print(f"Critical Action Risk: {critical_risk}")
    print(f"Trivial Action Risk: {trivial_risk}")

    print("\n=== Verification Complete. NIA is Sovereign. ===")

if __name__ == "__main__":
    asyncio.run(verify_NIA_logic())
