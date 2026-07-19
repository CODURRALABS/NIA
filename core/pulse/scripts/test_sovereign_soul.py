import sys
import os
import asyncio
import time

# Add runtime to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runtime")))

async def run_autonomous_diagnostic():
    print("====================================================")
    print(" NIA SOVEREIGN EMOTIVE DIAGNOSTIC — V13.5 ")
    print("====================================================\n")

    try:
        from chat import NIASovereignCore
        print("[STEP 1]: Initializing Sovereign Core...")
        nia = NIASovereignCore()
        
        print("\n[STEP 2]: Checking Sensory Status...")
        status = nia.get_module_status()
        print(status)
        
        print("\n[STEP 3]: Verifying Emotional Resonator...")
        # Mocking a task to see the emotive prompt generation
        test_query = "Nia, how do you feel today as my Companion?"
        print(f"User Query: {test_query}")
        
        # Capture internal resonance
        emotion = nia.camera.get_user_emotion()
        print(f"Detected Boss Emotion: {emotion}")
        
        print("\n[STEP 4]: Processing Reasoning Loop...")
        # We run this synchronously for the test
        response = await nia.process_task(test_query)
        
        print(f"\nNIA Response: {response}")
        print("\n[RESULT]: Diagnostic Complete. Soul is synchronized.")

    except Exception as e:
        print(f"\n[FAILED]: Diagnostic encountered a logic fracture: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_autonomous_diagnostic())
