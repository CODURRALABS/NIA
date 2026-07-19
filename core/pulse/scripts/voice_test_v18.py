import sys
import os
import asyncio
import logging

# Set up path to agent-core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'runtime')))

from audio_soul import AudioSoul

async def test_voice_modality():
    print("\n[V18 BENCHMARK]: Test 2 - Voice (Sovereign Vocal Entity)")
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 1. Initialize AudioSoul
        print("[VOICE]: Initializing Neural Audio Soul...")
        audio = AudioSoul()
        
        if not audio.ready:
            print("[RESULT]: Voice Modality FAIL: Neural engine not ready (Check dependencies/models).")
            return False
            
        # 2. Perform Vocal Synthesis
        test_text = "Neural vocal entity online. Integrity check passed."
        print(f"[VOICE]: Synthesizing test phrase: '{test_text}'")
        audio.speak(test_text)
        
        # Give some time for synthesis thread logic to start
        await asyncio.sleep(2)
        
        print("[RESULT]: Voice Modality PASS (Neural Sync Active).")
        return True
    except Exception as e:
        print(f"[RESULT]: Voice Modality FAIL: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_voice_modality())
