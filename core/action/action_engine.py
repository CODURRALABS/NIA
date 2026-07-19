"""
NIA ActionEngine — The Hands
Controls mouse, keyboard, and windows exactly like a human.
Hardware-level input injection via SendInput.
App-level control via UIA and pywinauto.
"""

import ctypes
import ctypes.wintypes
import time
import subprocess
import os
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import IntEnum

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# SendInput structures
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVEABS = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
KEYEVENTF_KEYUP = 0x0002
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
WHEEL_DELTA = 120
SCREEN_W = user32.GetSystemMetrics(0)
SCREEN_H = user32.GetSystemMetrics(1)


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.wintypes.LONG),
        ("dy", ctypes.wintypes.LONG),
        ("mouseData", ctypes.wintypes.DWORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.wintypes.WORD),
        ("wScan", ctypes.wintypes.WORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.wintypes.DWORD), ("union", INPUT_UNION)]


class Mouse:
    """Hardware-level mouse control."""

    @staticmethod
    def _send_input(*inputs: INPUT):
        n = len(inputs)
        arr = (INPUT * n)(*inputs)
        user32.SendInput(n, ctypes.pointer(arr), ctypes.sizeof(INPUT))

    @staticmethod
    def move(x: int, y: int, absolute: bool = True, duration: float = 0.0):
        """Move mouse to position. absolute=True uses screen coordinates."""
        if duration > 0:
            # Smooth movement
            current = Mouse.position()
            steps = max(int(duration / 0.01), 1)
            dx = (x - current[0]) / steps
            dy = (y - current[1]) / steps
            for i in range(steps):
                mx = int(current[0] + dx * (i + 1))
                my = int(current[1] + dy * (i + 1))
                if absolute:
                    nx = int(mx * 65535 / SCREEN_W)
                    ny = int(my * 65535 / SCREEN_H)
                else:
                    nx, ny = mx, my
                inp = INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(
                    dx=nx, dy=ny, dwFlags=MOUSEEVENTF_MOVEABS
                )))
                Mouse._send_input(inp)
                time.sleep(0.01)
        else:
            if absolute:
                nx = int(x * 65535 / SCREEN_W)
                ny = int(y * 65535 / SCREEN_H)
            else:
                nx, ny = x, y
            inp = INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(
                dx=nx, dy=ny, dwFlags=MOUSEEVENTF_MOVEABS
            )))
            Mouse._send_input(inp)

    @staticmethod
    def click(x: Optional[int] = None, y: Optional[int] = None, button: str = "left"):
        """Click at position (or current position if None)."""
        if x is not None and y is not None:
            Mouse.move(x, y)
            time.sleep(0.05)

        if button == "left":
            down, up = MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP
        elif button == "right":
            down, up = MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP
        elif button == "middle":
            down, up = MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP
        else:
            return

        inp_down = INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(dwFlags=down)))
        inp_up = INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(dwFlags=up)))
        Mouse._send_input(inp_down, inp_up)

    @staticmethod
    def double_click(x: Optional[int] = None, y: Optional[int] = None):
        Mouse.click(x, y)
        time.sleep(0.05)
        Mouse.click()

    @staticmethod
    def scroll(x: Optional[int] = None, y: Optional[int] = None, delta: int = 3):
        """Scroll wheel. Positive = up, negative = down."""
        if x is not None and y is not None:
            Mouse.move(x, y)
            time.sleep(0.02)
        inp = INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(
            mouseData=delta * WHEEL_DELTA,
            dwFlags=MOUSEEVENTF_WHEEL
        )))
        Mouse._send_input(inp)

    @staticmethod
    def drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.3):
        """Click and drag from (x1,y1) to (x2,y2)."""
        Mouse.move(x1, y1)
        time.sleep(0.05)
        inp_down = INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(dwFlags=MOUSEEVENTF_LEFTDOWN))
        )
        Mouse._send_input(inp_down)
        Mouse.move(x2, y2, duration=duration)
        time.sleep(0.02)
        inp_up = INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(dwFlags=MOUSEEVENTF_LEFTUP)))
        Mouse._send_input(inp_up)

    @staticmethod
    def position() -> Tuple[int, int]:
        """Get current mouse position."""
        pt = ctypes.wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return (pt.x, pt.y)


class Keyboard:
    """Hardware-level keyboard control."""

    VK_MAP = {
        "enter": 0x0D, "return": 0x0D,
        "tab": 0x09,
        "escape": 0x1B, "esc": 0x1B,
        "space": 0x20,
        "backspace": 0x08,
        "delete": 0x2E, "del": 0x2E,
        "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
        "home": 0x24, "end": 0x23,
        "pageup": 0x21, "pgup": 0x21,
        "pagedown": 0x22, "pgdn": 0x22,
        "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
        "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
        "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
        "ctrl": 0x11, "lctrl": 0x11, "rctrl": 0xA3,
        "alt": 0x12, "lalt": 0xA4, "ralt": 0xA5,
        "shift": 0x10, "lshift": 0xA0, "rshift": 0xA1,
        "win": 0x5B, "lwin": 0x5B, "rwin": 0x5C,
        "capslock": 0x14,
    }

    @staticmethod
    def _send_input(*inputs: INPUT):
        n = len(inputs)
        arr = (INPUT * n)(*inputs)
        user32.SendInput(n, ctypes.pointer(arr), ctypes.sizeof(INPUT))

    @staticmethod
    def _vk_to_input(vk: int, key_up: bool = False) -> INPUT:
        flags = KEYEVENTF_KEYUP if key_up else 0
        return INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(
            wVk=vk, dwFlags=flags
        )))

    @staticmethod
    def press(vk: int):
        """Press and release a key by virtual key code."""
        inp_down = Keyboard._vk_to_input(vk, key_up=False)
        inp_up = Keyboard._vk_to_input(vk, key_up=True)
        Keyboard._send_input(inp_down, inp_up)

    @staticmethod
    def hotkey(*keys: str):
        """Press a key combination. hotkey('ctrl', 'c') = Ctrl+C."""
        vks = [Keyboard.VK_MAP.get(k.lower(), ord(k.upper())) for k in keys]
        # Press all in order
        for vk in vks:
            Keyboard._send_input(Keyboard._vk_to_input(vk, key_up=False))
            time.sleep(0.02)
        # Release in reverse
        for vk in reversed(vks):
            Keyboard._send_input(Keyboard._vk_to_input(vk, key_up=True))
            time.sleep(0.02)

    @staticmethod
    def type_text(text: str, delay: float = 0.02):
        """Type text character by character, like a human typing."""
        for char in text:
            # Use SendInput with Unicode
            inp_down = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(
                wVk=0, wScan=ord(char), dwFlags=0x0004  # KEYEVENTF_UNICODE
            )))
            inp_up = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(
                wVk=0, wScan=ord(char), dwFlags=0x0004 | KEYEVENTF_KEYUP
            )))
            Keyboard._send_input(inp_down, inp_up)
            if delay > 0:
                time.sleep(delay)

    @staticmethod
    def type_keys(keys: str, delay: float = 0.02):
        """Type a string of key names separated by '+'. e.g. 'ctrl+a'."""
        Keyboard.hotkey(*keys.split("+"))


class WindowManager:
    """Find, focus, move, resize windows."""

    @staticmethod
    def open(app_path: str, args: str = "") -> Optional[int]:
        """Launch an application and return its PID."""
        cmd = f'"{app_path}" {args}' if args else f'"{app_path}"'
        proc = subprocess.Popen(cmd, shell=True)
        time.sleep(1.0)  # Wait for window to appear
        return proc.pid

    @staticmethod
    def find_and_focus(title_partial: str) -> bool:
        """Find a window by partial title and bring it to foreground."""
        try:
            from core.sense.desktop_capture import WindowEnumerator
            win = WindowEnumerator.find_window(title_partial)
            if win:
                WindowEnumerator.focus_window(win.hwnd)
                time.sleep(0.3)
                return True
        except ImportError:
            try:
                from sense.desktop_capture import WindowEnumerator
                win = WindowEnumerator.find_window(title_partial)
                if win:
                    WindowEnumerator.focus_window(win.hwnd)
                    time.sleep(0.3)
                    return True
            except ImportError:
                print("[WindowManager] desktop_capture module not available")
        return False

    @staticmethod
    def set_foreground(hwnd: int):
        """Force a window to the foreground."""
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.2)

    @staticmethod
    def get_foreground_title() -> str:
        """Get the title of the currently active window."""
        hwnd = user32.GetForegroundWindow()
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        return buf.value

    @staticmethod
    def maximize(hwnd: int):
        user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE

    @staticmethod
    def minimize(hwnd: int):
        user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE

    @staticmethod
    def restore(hwnd: int):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE


class ActionEngine:
    """
    Unified action interface — NIA's hands.
    Combines mouse, keyboard, window management, and app launching.
    """

    def __init__(self):
        self.mouse = Mouse()
        self.keyboard = Keyboard()
        self.windows = WindowManager()
        self._action_log: List[dict] = []

    def execute(self, action: dict) -> dict:
        """
        Execute an action described as a dict.
        Action format: {"type": "...", "params": {...}}

        Types:
          - click:     {x, y, button?}
          - double:    {x, y}
          - type:      {text, delay?}
          - hotkey:    {keys}          e.g. "ctrl+c"
          - scroll:    {x?, y?, delta?}
          - drag:      {x1, y1, x2, y2}
          - open:      {path, args?}
          - focus:     {title}
          - move:      {x, y}
        """
        action_type = action.get("type")
        params = action.get("params", {})
        result = {"success": False, "action": action_type}

        try:
            if action_type == "click":
                self.mouse.click(params.get("x"), params.get("y"), params.get("button", "left"))
                result["success"] = True

            elif action_type == "double_click":
                self.mouse.double_click(params.get("x"), params.get("y"))
                result["success"] = True

            elif action_type == "type":
                self.keyboard.type_text(params.get("text", ""), params.get("delay", 0.02))
                result["success"] = True

            elif action_type == "hotkey":
                self.keyboard.hotkey(*params.get("keys", "").split("+"))
                result["success"] = True

            elif action_type == "scroll":
                self.mouse.scroll(params.get("x"), params.get("y"), params.get("delta", 3))
                result["success"] = True

            elif action_type == "drag":
                self.mouse.drag(
                    params["x1"], params["y1"],
                    params["x2"], params["y2"],
                    params.get("duration", 0.3)
                )
                result["success"] = True

            elif action_type == "open":
                pid = self.windows.open(params["path"], params.get("args", ""))
                result["success"] = pid is not None
                result["pid"] = pid

            elif action_type == "focus":
                result["success"] = self.windows.find_and_focus(params["title"])

            elif action_type == "move":
                self.mouse.move(params["x"], params["y"])
                result["success"] = True

            else:
                result["error"] = f"Unknown action type: {action_type}"

        except Exception as e:
            result["error"] = str(e)

        self._action_log.append({**result, "time": time.time()})
        return result

    def safe_action(self, action: dict, verify_fn=None, timeout: float = 5.0) -> dict:
        """
        Execute an action and optionally verify it worked.
        If verify_fn returns False, retry or report failure.
        """
        start = time.time()
        last_result = None

        while time.time() - start < timeout:
            last_result = self.execute(action)
            if last_result["success"]:
                if verify_fn is None or verify_fn():
                    return last_result
                time.sleep(0.3)
            else:
                break

        return last_result or {"success": False, "error": "Timeout"}

    @property
    def recent_actions(self) -> List[dict]:
        return self._action_log[-20:]
