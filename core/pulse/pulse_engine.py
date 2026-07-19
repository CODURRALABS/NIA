import os
import sys
import socket
import hashlib
import time
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from zeroconf import ServiceInfo, Zeroconf
import uvicorn

# Ensure the runtime is discoverable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "runtime"))
from chat import NIASovereignCore

app = FastAPI(title="NIA Hybrid Reasoning Runtime - V13")

# Enable CORS for the Web Hub
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Sovereign Initialization
# We initialize the core globally so it stays in VRAM.
nia_core: Optional[NIASovereignCore] = None

@app.on_event("startup")
async def startup_event():
    global nia_core
    nia_core = NIASovereignCore()
    print("\n[RUNTIME]: Hybrid Reasoning Runtime initialized and anchored.")

# 2. Sovereign Hash ID (DHT P2P Identity)
def generate_nia_hash_id():
    hostname = socket.gethostname()
    raw_id = f"NIA_SOVEREIGN_{hostname}_{time.time()}"
    return hashlib.sha256(raw_id.encode()).hexdigest()

NIA_HASH_ID = generate_nia_hash_id()

# 3. Pulse Routes (Web Hub API)
@app.get("/")
async def root():
    return {
        "runtime": "NIA Hybrid Reasoning Hub",
        "version": "V13-STABLE",
        "hash_id": NIA_HASH_ID,
        "status": "OPERATIONAL"
    }

@app.post("/pulse/chat")
async def chat_endpoint(request: Request):
    global nia_core
    if not nia_core:
        return {"response": "NIA Engine Initializing..."}
    
    data = await request.json()
    prompt = data.get("prompt", "")
    
    print(f"\n[BRIDGE]: Received request from Web Hub: '{prompt[:50]}...'")
    
    # Process reasoning
    response = await nia_core.process_task(prompt)
    
    # Auto-speak if requested (standard for V13)
    nia_core.audio.speak(response)
    
    return {"response": response}

@app.post("/pulse/speak")
async def speak_endpoint(request: Request):
    global nia_core
    if not nia_core:
        return {"status": "error", "message": "Engine not ready"}
    
    data = await request.json()
    text = data.get("text", "")
    nia_core.voice.speak(text)
    return {"status": "success"}

# 4. Neural Mesh (P2P Discovery)
class SovereignMesh:
    def __init__(self, port=8000):
        self.zeroconf = Zeroconf()
        self.port = port
        self.info = ServiceInfo(
            "_nia-mesh._tcp.local.",
            "NIA Unified Hub._nia-mesh._tcp.local.",
            addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
            port=self.port,
            properties={'hash': NIA_HASH_ID, 'v': 'V12'},
            server=f"nia-{NIA_HASH_ID[:8]}.local.",
        )

    def broadcast(self):
        self.zeroconf.register_service(self.info)

    def stop(self):
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()

if __name__ == "__main__":
    mesh = SovereignMesh()
    mesh.broadcast()
    
    print(f"╔" + "═"*55 + "╗")
    print(f"║      NIA UNIFIED PULSE HUB (V12 - API ACTIVE)         ║")
    print(f"║      Hash ID: {NIA_HASH_ID[:12]}...                 ║")
    print(f"╚" + "═"*55 + "╝\n")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        mesh.stop()
