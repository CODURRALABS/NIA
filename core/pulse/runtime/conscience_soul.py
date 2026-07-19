import time
import threading
import logging
import pygetwindow as gw
from typing import List, Optional

logger = logging.getLogger("ConscienceSoul")

class ConscienceSoul:
    """
    The 'Guardian' of NIA.
    V13.9 - The Watcher: Proactive Monitoring & 4-Hour Probability Simulation.
    """
    def __init__(self, distraction_apps: List[str] = None):
        self.distractions = distraction_apps or ["YouTube", "Netflix", "Prime Video", "Disney+", "VLC", "Movies & TV"]
        self.active = False
        self.monitoring_thread = None
        self.simulation_thread = None
        self.start_times = {} # Track app usage duration
        self.intervention_threshold = 1800 # 30 mins default
        
        # Simulation Logic
        self.simulation_active = False
        self.security_mode = True
        self.social_mode = True
        
        # Memory-driven focus (e.g. CUET Exams)
        self.priority_focus = False 
        
    def start_monitoring(self, on_trigger_callback):
        """Starts the background conscience and simulation threads."""
        self.active = True
        self.on_trigger = on_trigger_callback
        
        # 1. Distraction Monitoring
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        
        # 2. Probability Simulation
        self.simulation_active = True
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        
        print("[CONSCIENCE]: Monitoring and Simulation active. I am watching the threads of your reality, Boss.")

    def _monitor_loop(self):
        while self.active:
            try:
                active_window = gw.getActiveWindow()
                if active_window and active_window.title:
                    title = active_window.title
                    is_distraction = any(d.lower() in title.lower() for d in self.distractions)
                    if is_distraction:
                        duration = time.time() - self.start_times.get(title, time.time())
                        if self.priority_focus or duration > self.intervention_threshold:
                            self.on_trigger("DISTRACTION", {"app": title, "duration": duration})
                            self.start_times[title] = time.time() + 600
                    else:
                        self.start_times = {}
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            time.sleep(10)

    def _simulation_loop(self):
        """Simulates the next 4 hours of local and social probability."""
        while self.simulation_active:
            try:
                # 1. Local Security Logic (Heuristic for now)
                if self.security_mode:
                    # In real usage, this would check CameraSoul for unknown faces
                    pass
                
                # 2. Social Dynamics Logic (Village Chess)
                if self.social_mode:
                    # Heuristic: If it's evening and user is at a 'Wedding' (from calendar/context)
                    # Trigger a proactive social cheat-code
                    pass

                # Simulate a 'Social Trap' or 'Security Breach'
                # For testing: random probability trigger
                import random
                if random.random() < 0.01: # 1% chance every check
                    self.on_trigger("SIMULATION", {"type": "SOCIAL", "msg": "Uncle X detected nearby. Probability of career interrogation: 85%."})
            except Exception as e:
                logger.error(f"Simulation error: {e}")
            time.sleep(30)

    def set_priority_focus(self, active: bool):
        self.priority_focus = active
        status = "CRITICAL (Exams Nearby)" if active else "Normal"
        print(f"[CONSCIENCE]: Focus Level updated to: {status}")

    def stop(self):
        self.active = False

if __name__ == "__main__":
    def test_trigger(app, duration):
        print(f"ALERT: Boss has been on {app} for {duration/60:.1f} minutes!")
        
    conscience = ConscienceSoul()
    conscience.set_priority_focus(True)
    conscience.start_monitoring(test_trigger)
    time.sleep(20)
    conscience.stop()
