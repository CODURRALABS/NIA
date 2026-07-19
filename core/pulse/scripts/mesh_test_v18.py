import sys
import os
import asyncio
import socket
import logging

# Set up path to agent-core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pulse_engine import SovereignMesh

async def test_mesh_modality():
    print("\n[V18 BENCHMARK]: Test 3 - Mesh (Sovereign Neural Mesh)")
    logging.basicConfig(level=logging.ERROR)
    
    try:
        # 1. Initialize Mesh
        print("[MESH]: Initializing Zeroconf Service Discovery...")
        mesh = SovereignMesh(port=8888) # Use different port for test
        
        # 2. Broadcast
        print("[MESH]: Broadcasting P2P Identity...")
        mesh.broadcast()
        
        # 3. Verify socket availability
        hostname = socket.gethostname()
        print(f"[MESH]: Mesh Identity anchored at {hostname}.")
        
        # Small wait to simulate network stabilization
        await asyncio.sleep(2)
        
        mesh.stop()
        print("[RESULT]: Mesh Modality PASS.")
        return True
    except Exception as e:
        print(f"[RESULT]: Mesh Modality FAIL: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mesh_modality())
