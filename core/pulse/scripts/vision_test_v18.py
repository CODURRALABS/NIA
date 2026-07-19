import sys
import os
import asyncio
import logging

# Set up path to agent-core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'runtime')))

from vision_soul import VisionSoul
from camera_soul import CameraSoul

async def test_vision_modality():
    print("\n[V18 BENCHMARK]: Test 1 - Vision (Sovereign Retina)")
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 1. Initialize Vision
        vision = VisionSoul()
        print("[VISION]: Initializing Screen Perception...")
        screen_data = vision.get_screen_context()
        print(f"[VISION]: Screen Context detected: {screen_data[:100]}...")
        
        # 2. Initialize Camera face count (for Socius Soul decision)
        camera = CameraSoul()
        print("[VISION]: Initializing Camera Pulse...")
        faces = camera.get_face_count()
        print(f"[VISION]: Face Count: {faces}")
        
        print("[RESULT]: Vision Modality PASS.")
        return True
    except Exception as e:
        print(f"[RESULT]: Vision Modality FAIL: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_vision_modality())
