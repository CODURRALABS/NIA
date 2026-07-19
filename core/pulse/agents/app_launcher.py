"""
AppLauncher: Opens, closes, and switches between Windows applications.
"""
import os
import subprocess
import logging
import time
try:
    import win32gui
    import win32con
    import win32api
except ImportError:
    win32gui = win32con = win32api = None

logger = logging.getLogger("AppLauncher")

class AppLauncher:
    def open_app(self, app_name_or_path: str):
        """Opens an app by name (using start command) or absolute path."""
        logger.info(f"Opening app: {app_name_or_path}")
        try:
            if os.path.isabs(app_name_or_path):
                subprocess.Popen(app_name_or_path)
            else:
                # Use Windows 'start' to find app in PATH or registered apps
                os.system(f'start "" "{app_name_or_path}"')
            return True
        except Exception as e:
            logger.error(f"Failed to open app: {e}")
            return False

    def close_app(self, app_name: str):
        """Closes an app by killing its process name."""
        logger.info(f"Closing app: {app_name}")
        try:
            os.system(f'taskkill /F /IM "{app_name}.exe"')
            return True
        except Exception as e:
            logger.error(f"Failed to close app: {e}")
            return False

    def switch_to_app(self, window_title_part: str):
        """Brings a window to the foreground by title substring."""
        if not win32gui:
            logger.error("win32gui not available.")
            return False

        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if window_title_part.lower() in title.lower():
                    logger.info(f"Found window '{title}', switching...")
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    return False # Stop enumeration
            return True

        try:
            win32gui.EnumWindows(callback, None)
            return True
        except Exception as e:
            # win32gui.EnumWindows raises error when callback returns False (intentional stop)
            return True
            
    def list_open_windows(self):
        """Returns a list of all visible window titles."""
        if not win32gui:
            return []
        titles = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    titles.append(title)
            return True
        win32gui.EnumWindows(callback, None)
        return titles

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    launcher = AppLauncher()
    launcher.open_app("notepad")
    time.sleep(2)
    print(f"Open Windows: {launcher.list_open_windows()[:5]}")
    launcher.switch_to_app("notepad")
