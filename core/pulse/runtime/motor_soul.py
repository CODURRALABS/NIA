import os
import subprocess
import ctypes
import logging
import threading
import time
from typing import Optional, Dict, Any

# Third-party hardware control
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    import screen_brightness_control as sbc
    import pyautogui
    from pynput.keyboard import Controller as KeyboardController
    from pynput.mouse import Controller as MouseController
    PYCAW_READY = True
    HANDS_READY = True
except ImportError:
    PYCAW_READY = False
    HANDS_READY = False

logger = logging.getLogger("MotorSoul")

class MotorSoul:
    """
    The 'Hands' of NIA. 
    V13.11 - Autonomous Operator: Physical App Agency & UI Mastery.
    """
    def __init__(self):
        print("[MOTOR]: Ignite. Executive Motor Skills (v13.11) initialized.")
        self.keyboard = KeyboardController() if HANDS_READY else None
        self.mouse = MouseController() if HANDS_READY else None
        pyautogui.PAUSE = 0.5
        pyautogui.FAILSAFE = True
        self.dev_workplace_default = os.path.expanduser("~/NIA_PROJECTS")
        if not os.path.exists(self.dev_workplace_default):
            os.makedirs(self.dev_workplace_default)

    def is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    # --- 1. Hardware Control ---
    
    def set_volume(self, level: int):
        """Sets master volume (0-100)."""
        if not PYCAW_READY: return
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
            # Level is 0.0 to 1.0
            volume.SetMasterVolumeLevelScalar(level / 100, None)
            print(f"[MOTOR]: Volume set to {level}%")
        except Exception as e:
            logger.error(f"Volume error: {e}")

    def set_brightness(self, level: int):
        """Sets screen brightness (0-100)."""
        if not PYCAW_READY: return
        try:
            sbc.set_brightness(level)
            print(f"[MOTOR]: Brightness set to {level}%")
        except Exception as e:
            logger.error(f"Brightness error: {e}")

    # --- 2. OS Navigation & Power ---
    
    def system_action(self, action: str):
        """Power management actions: lock, sleep, shutdown, restart."""
        actions = {
            "lock": "rundll32.exe user32.dll,LockWorkStation",
            "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
            "shutdown": "shutdown /s /t 0",
            "restart": "shutdown /r /t 0"
        }
        
        cmd = actions.get(action.lower())
        if cmd:
            print(f"[MOTOR]: Executing System Command: {action}")
            subprocess.run(cmd, shell=True)

    def change_wallpaper(self, image_path: str):
        """Changes Windows desktop wallpaper."""
        if not os.path.exists(image_path):
            return False
        try:
            # SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            print(f"[MOTOR]: Wallpaper updated to {image_path}")
            return True
        except Exception as e:
            logger.error(f"Wallpaper error: {e}")
            return False

    # --- 3. NetPulse (Connectivity) ---
    
    def toggle_wifi(self, state: bool):
        """Toggles WiFi via PowerShell (Requires Admin for some cards)."""
        status = "Enabled" if state else "Disabled"
        cmd = f"Get-NetAdapter | Where-Object {{$_.Name -like '*Wi-Fi*'}} | {status}-NetAdapter -Confirm:$false"
        try:
            subprocess.run(["powershell", "-Command", cmd], capture_output=True)
            print(f"[MOTOR]: WiFi {status}")
        except Exception as e:
            logger.error(f"WiFi toggle error: {e}")

    def toggle_airplane_mode(self, state: bool):
        """Opens Airplane settings (API toggle is limited in Python/Win11)."""
        # User requested opening in background/automatic
        # We use URI to jump to settings
        subprocess.run("start ms-settings:network-airplanemode", shell=True)
        print("[MOTOR]: Jumped to Airplane Mode settings.")

    # --- 5. Application Agency (Workplace Hands) ---
    
    def open_app(self, app_name: str, visible: bool = True):
        """Opens common apps and focuses them."""
        apps = {
            "notepad": "notepad.exe",
            "vscode": "code",
            "chrome": "chrome.exe",
            "terminal": "powershell.exe",
            "word": "winword.exe"
        }
        cmd = apps.get(app_name.lower(), app_name)
        
        try:
            if visible:
                os.startfile(cmd)
                print(f"[MOTOR]: Visible Launch: {app_name}")
            else:
                subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"[MOTOR]: Background Launch: {app_name}")
            return True
        except Exception as e:
            logger.error(f"App launch error: {e}")
            return False

    def write_text(self, text: str, mode: str = "typing"):
        """Types text into the active window."""
        if not HANDS_READY: return
        
        if mode == "typing":
            pyautogui.write(text, interval=0.05)
        elif mode == "hotkey":
            pyautogui.hotkey(*text.split("+"))
            
    def move_to_element(self, x: int, y: int):
        """Moves mouse to coordinates and clicks."""
        if not HANDS_READY: return
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()

    def autonomous_notepad_task(self, content: str, filename: str = "nia_lyrics.txt"):
        """Example: Opens notepad, writes content, and saves."""
        # This is a 'Visible' task as requested
        self.open_app("notepad", visible=True)
        time.sleep(1) # Wait for open
        self.write_text(content)
        time.sleep(0.5)
        # Save sequence
        pyautogui.hotkey("ctrl", "s")
        time.sleep(0.5)
        pyautogui.write(filename)
        pyautogui.press("enter")
        print(f"[MOTOR]: Notepad task complete: {filename}")

if __name__ == "__main__":
    motor = MotorSoul()
    # motor.set_volume(20)
    # motor.clear_storage_junk()
