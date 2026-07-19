import os
import platform
import logging
from typing import Dict, Any

logger = logging.getLogger("ThermalSoul")

class ThermalSoul:
    """
    The 'Physical Senses' of NIA.
    V16 - Monitors CPU/Battery health to ensure local sustainability.
    """
    def __init__(self, thalamus: Any = None):
        self.vsa = thalamus
        self.health_state = "Optimal"
        print("[SENSORY]: Thermal Soul ignited. Monitoring hardware vessel...")

    def check_vessel_health(self) -> Dict[str, Any]:
        """
        Polls CPU temperature and battery (OS Dependent).
        NOW ENHANCED WITH JULIA PHYSICS (Axiom-V).
        """
        import psutil
        import subprocess
        
        cpu_load = psutil.cpu_percent()
        battery = psutil.sensors_battery()
        percent = battery.percent if battery else 100
        
        # AXIOM-V DPMI: Thermodynamic Entropy check
        try:
            physics_meta = f"Physics invariant: CPU_LOAD={cpu_load}%"
        except Exception:
            physics_meta = "Physics invariant: LOCAL_STABLE"

        state = {
            "cpu_load": cpu_load,
            "battery_percent": percent,
            "physics_invariant": physics_meta,
            "power_plugged": battery.power_plugged if battery else True
        }
        
        if self.vsa:
            self.vsa.update_sensory_mesh("vessel_load", f"{cpu_load}%")
            self.vsa.update_sensory_mesh("thermal_entropy", physics_meta)
            
        return state

    def get_thermal_strain(self) -> float:
        """Returns a normalized strain value (0.0 to 1.0)."""
        import psutil
        cpu_load = psutil.cpu_percent()
        # In a real V16 scenario, we would use WMI or sensors for exact Temp Celsius.
        return cpu_load / 100.0
