import socket
import threading
import json
import time
import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from dotenv import load_dotenv

load_dotenv()

class ShadowMeshNode:
    """
    NIA Sovereign Shadow Mesh Node v1.0
    A real-time, decentralized P2P node for Logic DNA synchronization.
    """
    def __init__(self, port=9000):
        self.node_id = os.getenv("NIA_SOVEREIGN_ID", "anonymous_node")
        self.port = port
        self.peers = set() # Set of (ip, port)
        self.logic_dna_log = []
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # MASTER KEY: Derived from Sovereign ID
        self.key = hashlib.sha256(self.node_id.encode()).digest()

    def start(self):
        self.running = True
        self.sock.bind(('', self.port))
        threading.Thread(target=self._listen, daemon=True).start()
        threading.Thread(target=self._broadcast_presence, daemon=True).start()
        print(f"[SHADOW MESH]: node {self.node_id[:8]} active on port {self.port}")

    def _listen(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                msg = json.loads(data.decode())
                
                if msg['type'] == 'presence':
                    if addr not in self.peers:
                        self.peers.add(addr)
                        print(f"[SHADOW MESH]: New Peer Discovered -> {addr}")
                
                elif msg['type'] == 'dna_sync':
                    self._handle_dna_sync(msg['dna'], msg['source'])
                    
            except Exception as e:
                pass

    def _broadcast_presence(self):
        while self.running:
            msg = {
                "type": "presence",
                "node_id": self.node_id,
                "timestamp": time.time()
            }
            # Broadcast to local subnet (simple discovery for home mesh)
            self.sock.sendto(json.dumps(msg).encode(), ('<broadcast>', self.port))
            time.sleep(10)

    def _encrypt(self, data: str) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        return cipher.iv + ct_bytes

    def _decrypt(self, data: bytes) -> str:
        iv = data[:16]
        ct = data[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ct), AES.block_size).decode()

    def sync_dna(self, dna_pattern):
        """Broadcasts an ENCRYPTED Logic DNA pattern to discovered peers."""
        msg_data = json.dumps({
            "dna": dna_pattern,
            "source": self.node_id,
            "timestamp": time.time()
        })
        encrypted_packet = self._encrypt(msg_data)
        
        final_msg = {
            "type": "dna_sync_v16",
            "payload": encrypted_packet.hex()
        }
        
        for peer in self.peers:
            try:
                self.sock.sendto(json.dumps(final_msg).encode(), peer)
            except:
                pass
        print(f"[SHADOW MESH]: Encrypted DNA Synchronized -> {dna_pattern[:16]}...")

    def _handle_dna_sync(self, dna, source):
        # Implement Distributed Consensus Math
        # If hash(dna) matches the sovereign bit-pattern protocol, commit to log
        self.logic_dna_log.append({"dna": dna, "source": source, "time": time.time()})
        print(f"[SHADOW MESH]: Received DNA from {source[:8]}: {dna[:16]}")

if __name__ == "__main__":
    node = ShadowMeshNode()
    node.start()
    while True:
        time.sleep(1)
