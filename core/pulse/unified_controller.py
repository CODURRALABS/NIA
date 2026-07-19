"""
Unified Controller: The Core of NIA's Sovereign Architecture.
Orchestrates the OpenManus Planner, UI-TARS Vision, 
AgenticSeek Network proxy, n8n workflows, and the LLM engine.
"""
import asyncio
import requests
import logging

logger = logging.getLogger("UnifiedController")

# Assuming absolute imports based on agent-core structure
from llm_engine import LLMEngine
from planning.openmanus_planner import OpenManusPlanner
from vision.dom_distillation import VisualDistiller
from network.agentic_seek import LocalProxy
from integrations.n8n_bridge import N8NBridge
from agents.device_controller import DeviceController
from skills.skill_generator import SkillGenerator
from runtime.agent_os import AgentOS
from runtime.mcp_bridge import MCPBridge

class UnifiedController:
    def __init__(self):
        print("\n=== Initializing NIA Sovereign Unified Controller ===")
        self.llm = LLMEngine() # Uses MultiProviderRouter
        self.planner = OpenManusPlanner()
        self.vision = VisualDistiller()
        self.network = LocalProxy()
        self.n8n = N8NBridge()
        self.device = DeviceController()
        self.skills = SkillGenerator()
        self.os = AgentOS()
        self.mcp = MCPBridge()
        print("=== NIA Sovereign OS Online ===\n")

    def _notify_pulse(self, active: bool):
        """Helper to sync NIA's mechanical state with the background PulseEngine."""
        try:
            requests.post(f"http://localhost:8000/pulse/action?active={str(active).lower()}", timeout=1)
        except Exception:
            pass # Pulse engine might not be running

    async def execute_complex_goal(self, user_command: str):
        """
        Orchestrates high-level goals using AgentOS and MCP.
        """
        print(f"\n[Sovereign Core] Planning Strategy for: {user_command}")
        
        # 1. Intelligence Graphing (Phase 19)
        graph = self.os.plan_goal(user_command)
        nodes = graph.get('nodes', [])
        print(f">> AgentOS generated graph with {len(nodes)} nodes.")

        # 2. Sequential Execution (Simplified for Phase 19)
        for node in nodes:
            task_desc = node.get('task')
            module = node.get('module', '').lower()
            print(f">> Executing Task Node [{node['id']}]: ({module}) {task_desc}")
            
            if module == "vision":
                self.device.vision.capture_viewport()
            elif module == "skills":
                self.skills.generate_skill(task_desc)
            elif module == "audio":
                # Audio feedback would happen here
                pass
            
            # Action Execution with Pulse Notification
            if "click" in task_desc.lower() or "open" in task_desc.lower():
                self._notify_pulse(True)
                # Note: Coordinate mapping is handled inside execute_action
                self.device.execute_action("click", {"x": 0.5, "y": 0.5}, verify=True)
                self._notify_pulse(False)
        
        print("[Sovereign Core] Intelligence Graph Execution Complete.")
        return {"status": "success", "graph_id": graph.get('graph_id')}

    async def start_autonomous_session(self, initial_goal: str):
        """Continuous Watch-Think-Act loop."""
        print(f"[Core] Starting Real-Time Autonomous Session: {initial_goal}")
        for i in range(3): # Safety: limited to 3 steps for now
            print(f"\n--- Step {i+1} ---")
            # 1. Capture and Analyze
            self.device.vision.capture_viewport()
            # 2. Decide and Act
            self._notify_pulse(True)
            self.device.execute_action("click", {"x": 0.1, "y": 0.1}, verify=True)
            self._notify_pulse(False)
            await asyncio.sleep(2)
        print("[Core] Session finalized.")

if __name__ == "__main__":
    controller = UnifiedController()
    asyncio.run(controller.execute_complex_goal("Open the web browser and click the search bar"))
