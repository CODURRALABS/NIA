import asyncio
import time
import logging

logger = logging.getLogger("ProactiveLoop")

class ProactiveOrchestrationUnit:
    """
    NIA Hybrid Proactive Orchestration Unit (V19).
    Monitors the environment via the sensory mesh and triggers interventions.
    """
    def __init__(self, core_engine, interval: float = 60.0):
        self.core = core_engine
        self.interval = interval
        self.running = False

    async def start(self):
        """Starts the proactive cycle with Vision-Awareness (V19)."""
        self.running = True
        logger.info(f"Proactive Loop started with interval: {self.interval}s")
        
        while self.running:
            try:
                # 1. Gather context from VSA Blackboard
                vision_data = getattr(self.core, 'last_vision_data', "")
                
                # 2. Heuristic Proactive Triggers
                intervention_needed = False
                intervention_msg = ""
                
                # Scenario A: Technical Error Detection
                if any(err in vision_data.lower() for err in ["error", "exception", "failed to", "traceback"]):
                    intervention_msg = "Boss, I noticed an error on your screen. Would you like me to analyze the cause and suggest a fix?"
                    intervention_needed = True
                
                # Scenario B: Productivity Guardian (Distraction Detection)
                elif any(site in vision_data.lower() for site in ["youtube", "instagram", "facebook", "twitter", "x.com"]):
                    # Simple check for 'Work Mode' (VSA state)
                    if "work" in self.core.vsa.get_unified_awareness().lower():
                        intervention_msg = "Boss, you're currently in 'Sovereign Work' mode, but I see social media on screen. Focus is power. Should I close this for you?"
                        intervention_needed = True

                # 3. Trigger NIA's Will
                if intervention_needed:
                    self.core.notifier.show_alert("Sovereign Intervention", intervention_msg)
                    self.core.voice.speak(intervention_msg)
                    # We don't automatically process a task unless the user responds, 
                    # but NIA has initiated the 'Guardian' protocol.
                
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Proactive Loop Error: {e}")
                await asyncio.sleep(10)

    def stop(self):
        self.running = False
        logger.info("Proactive Loop stopped.")

if __name__ == "__main__":
    # Test stub
    print("Sovereign Proactive Heartbeat ready.")
