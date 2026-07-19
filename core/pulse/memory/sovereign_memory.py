"""
SovereignMemory implementation for NIA (Mem0 Logic).
Connects to Supabase to store and retrieve vector embeddings and text insights.
"""
import os
import json
from supabase import create_client, Client

class SovereignMemory:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            print("[Memory Warning] SUPABASE_URL or SUPABASE_ANON_KEY missing. Running in disconnected mode.")
            self.supabase = None
        else:
            try:
                self.supabase: Client = create_client(self.url, self.key)
                print("[Memory] SovereignMemory initialized via Supabase.")
            except Exception as e:
                print(f"[Memory Error] Failed to init Supabase: {e}")
                self.supabase = None
                
    def _generate_mock_embedding(self, content: str) -> list[float]:
        """Creates a mock 1536-dim vector for pgvector compatability before actual embedding models are linked."""
        return [0.01 for _ in range(1536)]

    def store_insight(self, topic: str, content: str, user_id: str = "local_admin"):
        """Upserts an insight into the 'nia_memory' table."""
        print(f"[Memory] Capturing Phase: {topic[:20]}...")
        if not self.supabase:
            print("[Memory Mock Route]: Database disconnected. Simulating API call.")
            return

        vector = self._generate_mock_embedding(content)
        
        try:
            data = {
                "user_id": user_id,
                "content": f"Topic: {topic} | Body: {content}",
                "vector_embedding": vector
            }
            # Upsert into Supabase table
            response = self.supabase.table("nia_memory").insert(data).execute()
            print(f"[Memory] Successfully upserted insight to Cloud DB. ID: {response.data[0]['id']}")
        except Exception as e:
            print(f"[Memory API Error] Failed to store insight: {e}")

    def retrieve_insight(self, query: str) -> str:
        """Retrieves an insight from Supabase."""
        if not self.supabase:
            return "Local disconnected mock memory: 12GB RAM strict limit rules apply."
            
        try:
            # Simple text match for now (pgvector similarity search requires RPC, simplifying for demo)
            response = self.supabase.table("nia_memory").select("content").limit(1).execute()
            if response.data:
                return response.data[0]['content']
            return "No memory found."
        except Exception as e:
             return f"[Memory API Error] Fetch failed: {e}"

if __name__ == "__main__":
    mem = SovereignMemory()
    mem.store_insight("PRD_Rule", "NIA must use 12GB to 8GB binary memory compression.")
    print("Retrieved:", mem.retrieve_insight("PRD"))
