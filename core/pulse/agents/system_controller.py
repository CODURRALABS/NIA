"""
SystemController: Controls Windows system settings like volume, brightness, and power.
"""
import logging
import os
import subprocess
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    AudioUtilities = None

logger = logging.getLogger("SystemController")

class SystemController:
    def __init__(self):
        self.volume_interface = self._get_volume_interface()

    def _get_volume_interface(self):
        if not AudioUtilities:
            return None
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            logger.error(f"Failed to get audio interface: {e}")
            return None

    def set_volume(self, level: int):
        """Sets system volume (0-100)."""
        if not self.volume_interface:
            return False
        try:
            # pycaw uses 0.0 to 1.0 or decibels
            scalar = max(0.0, min(1.0, level / 100.0))
            self.volume_interface.SetMasterVolumeLevelScalar(scalar, None)
            logger.info(f"Volume set to {level}%")
            return True
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False

    def get_volume(self):
        if not self.volume_interface:
            return 0
        return int(self.volume_interface.GetMasterVolumeLevelScalar() * 100)

    def set_brightness(self, level: int):
        """Sets monitor brightness using WMI/PowerShell."""
        logger.info(f"Setting brightness to {level}%")
        try:
            cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
            subprocess.run(["powershell", "-Command", cmd], check=True)
            return True
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
            return False

    def toggle_wifi(self, state: bool):
        status = "Enabled" if state else "Disabled"
        logger.info(f"Setting Wifi to {status}")
        try:
            cmd = f"Get-NetAdapter | Where-Object {{$_.Name -match 'Wi-Fi'}} | {status}-NetAdapter -Confirm:$false"
            subprocess.run(["powershell", "-Command", cmd], check=True)
            return True
        except Exception as e:
            logger.error(f"Error toggling wifi: {e}")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys_ctrl = SystemController()
    print(f"Current Volume: {sys_ctrl.get_volume()}%")
    sys_ctrl.set_volume(50)
