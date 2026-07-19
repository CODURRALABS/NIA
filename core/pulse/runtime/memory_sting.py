import os
import json
import sqlite3

class SovereignMemoryGraph:
    """
    Nebulara-Graph inspired local RAG architecture.
    Maps relationships between files, projects, and intents.
    """
    def __init__(self, db_path="runtime/sovereign_graph.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                type TEXT,
                metadata TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                source TEXT,
                target TEXT,
                relation TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(source) REFERENCES nodes(id),
                FOREIGN KEY(target) REFERENCES nodes(id)
            )
        """)
        self.conn.commit()

    def add_node(self, node_id, node_type, metadata=None):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO nodes VALUES (?, ?, ?)", 
                       (node_id, node_type, json.dumps(metadata or {})))
        self.conn.commit()

    def add_relation(self, source, target, relation):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO relations (source, target, relation) VALUES (?, ?, ?)", 
                       (source, target, relation))
        self.conn.commit()

    def query(self, cypher_like_query):
        """
        MATCH (p:Project)-[:DEVELOPED_BY]->(u:Ayush)
        Simplified SQL implementation for Sovereign RAG.
        """
        # Logic for parsing simple relations
        print(f"Querying Sovereign Graph: {cypher_like_query}")
        return []

    def export_map(self, output_path="KNOWLEDGE_MAP.json"):
        """
        Visualize the first 1,000 nodes and relationships.
        """
        cursor = self.conn.cursor()
        nodes = cursor.execute("SELECT * FROM nodes LIMIT 1000").fetchall()
        rels = cursor.execute("SELECT * FROM relations LIMIT 1000").fetchall()
        
        knowledge_map = {
            "nodes": [{"id": n[0], "type": n[1]} for n in nodes],
            "relations": [{"source": r[0], "target": r[1], "type": r[2]} for r in rels]
        }
        
        with open(output_path, "w") as f:
            json.dump(knowledge_map, f, indent=4)
        print(f"Knowledge Map exported to {output_path}")

if __name__ == "__main__":
    graph = SovereignMemoryGraph()
    graph.add_node("Project_NIA", "Project", {"status": "Construction"})
    graph.add_node("Ayush", "Sovereign")
    graph.add_relation("Project_NIA", "Ayush", "DEVELOPED_BY")
    
    graph.export_map()
    print("Sovereign Memory Graph Layer Active (Nebulara-Graph Protocol).")
