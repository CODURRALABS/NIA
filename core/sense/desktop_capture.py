"""
NIA SenseEngine — Live Screen Capture
Captures the desktop as a continuous stream using DXGI Desktop Duplication.
Falls back to Win32 GDI for older hardware.
No screenshots. No OCR. Raw pixel stream, frame by frame, like your eyes see.
"""

import ctypes
import ctypes.wintypes
import numpy as np
import time
import threading
import queue
import struct
from typing import Optional, Tuple, Generator
from dataclasses import dataclass

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
dwm32 = ctypes.windll.dwmapi


@dataclass
class Frame:
    """A single captured frame from the desktop."""
    pixels: np.ndarray       # HxWx4 BGRA numpy array
    timestamp: float         # Time of capture
    width: int
    height: int
    window_title: str = ""   # Active window title
    window_handle: int = 0   # HWND of active window


class DesktopCapture:
    """
    Real-time desktop capture using Win32 APIs.
    Captures frames as a continuous stream — not discrete screenshots.
    Designed for low latency (<16ms per frame).
    """

    def __init__(self, target_fps: int = 30, capture_cursor: bool = True):
        self.target_fps = target_fps
        self.capture_cursor = capture_cursor
        self.frame_interval = 1.0 / target_fps
        self._running = False
        self._frame_queue: queue.Queue = queue.Queue(maxsize=10)
        self._latest_frame: Optional[Frame] = None
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._stats = {
            "frames_captured": 0,
            "fps_actual": 0.0,
            "avg_frame_ms": 0.0,
        }
        self._last_fps_time = time.time()
        self._frame_count_in_second = 0

        # Win32 setup
        self._screen_width = user32.GetSystemMetrics(0)
        self._screen_height = user32.GetSystemMetrics(1)

        # Create device contexts
        self._desktop_hdc = user32.GetDC(0)  # Desktop DC
        self._memory_hdc = gdi32.CreateCompatibleDC(self._desktop_hdc)
        self._bitmap = gdi32.CreateCompatibleBitmap(
            self._desktop_hdc, self._screen_width, self._screen_height
        )
        gdi32.SelectObject(self._memory_hdc, self._bitmap)

        # BITMAPINFO for DIB section
        self._bmi = ctypes.wintypes.BITMAPINFOHEADER()
        self._bmi.biSize = ctypes.sizeof(self._bmi)
        self._bmi.biWidth = self._screen_width
        self._bmi.biHeight = -self._screen_height  # Top-down
        self._bmi.biPlanes = 1
        self._bmi.biBitCount = 32
        self._bmi.biCompression = 0  # BI_RGB

    def start(self):
        """Start the live capture stream."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        print(f"[SENSE] Live stream started — {self._screen_width}x{self._screen_height} @ {self.target_fps}fps")

    def stop(self):
        """Stop the capture stream."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        gdi32.DeleteObject(self._bitmap)
        gdi32.DeleteDC(self._memory_hdc)
        user32.ReleaseDC(0, self._desktop_hdc)
        print(f"[SENSE] Stream stopped. {self._stats['frames_captured']} frames captured.")

    def get_latest_frame(self) -> Optional[Frame]:
        """Get the most recent frame without blocking."""
        with self._lock:
            return self._latest_frame

    def get_frame_stream(self) -> Generator[Frame, None, None]:
        """Yield frames as they arrive — the live stream."""
        while self._running:
            try:
                frame = self._frame_queue.get(timeout=0.1)
                yield frame
            except queue.Empty:
                continue

    def read_region(self, x: int, y: int, w: int, h: int) -> np.ndarray:
        """Read a specific region of the screen as BGRA pixels."""
        region_hdc = gdi32.CreateCompatibleDC(self._desktop_hdc)
        region_bmp = gdi32.CreateCompatibleBitmap(self._desktop_hdc, w, h)
        gdi32.SelectObject(region_hdc, region_bmp)
        gdi32.BitBlt(region_hdc, 0, 0, w, h, self._desktop_hdc, x, y, 0x00CC0020)  # SRCCOPY

        buf = ctypes.create_string_buffer(w * h * 4)
        gdi32.GetDIBits(region_hdc, region_bmp, 0, h, buf, ctypes.byref(self._bmi), 0)
        pixels = np.frombuffer(buf, dtype=np.uint8).reshape(h, w, 4)

        gdi32.DeleteObject(region_bmp)
        gdi32.DeleteDC(region_hdc)
        return pixels

    def _capture_loop(self):
        """The main capture loop — runs continuously, producing frames."""
        buf = ctypes.create_string_buffer(self._screen_width * self._screen_height * 4)

        while self._running:
            loop_start = time.time()

            # Capture the desktop
            gdi32.BitBlt(
                self._memory_hdc, 0, 0,
                self._screen_width, self._screen_height,
                self._desktop_hdc, 0, 0,
                0x00CC0020  # SRCCOPY
            )

            # Extract pixels into numpy array
            gdi32.GetDIBits(
                self._memory_hdc, self._bitmap, 0,
                self._screen_height, buf,
                ctypes.byref(self._bmi), 0
            )
            pixels = np.frombuffer(buf, dtype=np.uint8).reshape(
                self._screen_height, self._screen_width, 4
            ).copy()

            # Get active window info
            hwnd = user32.GetForegroundWindow()
            title_buf = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(hwnd, title_buf, 256)

            now = time.time()
            frame = Frame(
                pixels=pixels,
                timestamp=now,
                width=self._screen_width,
                height=self._screen_height,
                window_title=title_buf.value,
                window_handle=hwnd,
            )

            # Update latest frame
            with self._lock:
                self._latest_frame = frame

            # Queue frame for stream consumers
            try:
                self._frame_queue.put_nowait(frame)
            except queue.Full:
                try:
                    self._frame_queue.get_nowait()
                    self._frame_queue.put_nowait(frame)
                except queue.Empty:
                    pass

            # Stats
            self._stats["frames_captured"] += 1
            self._frame_count_in_second += 1
            elapsed = now - self._last_fps_time
            if elapsed >= 1.0:
                self._stats["fps_actual"] = self._frame_count_in_second / elapsed
                self._frame_count_in_second = 0
                self._last_fps_time = now

            frame_ms = (time.time() - loop_start) * 1000
            self._stats["avg_frame_ms"] = (
                self._stats["avg_frame_ms"] * 0.95 + frame_ms * 0.05
            )

            # Sleep to maintain target FPS
            sleep_time = self.frame_interval - (time.time() - loop_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

    @property
    def stats(self):
        return self._stats.copy()


class WindowEnumerator:
    """Enumerate and manage windows — NIA's way of knowing what's running."""

    @dataclass
    class WindowInfo:
        hwnd: int
        title: str
        class_name: str
        rect: Tuple[int, int, int, int]  # left, top, right, bottom
        is_visible: bool
        pid: int

    @staticmethod
    def list_windows() -> list:
        """Get all visible windows."""
        windows = []

        def enum_callback(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True

            title_buf = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(hwnd, title_buf, 256)
            title = title_buf.value.strip()
            if not title:
                return True

            class_buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_buf, 256)

            rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))

            # Get PID
            pid = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            windows.append(WindowEnumerator.WindowInfo(
                hwnd=hwnd,
                title=title,
                class_name=class_buf.value,
                rect=(rect.left, rect.top, rect.right, rect.bottom),
                is_visible=True,
                pid=pid.value,
            ))
            return True

        ENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        user32.EnumWindows(ENUMPROC(enum_callback), 0)
        return windows

    @staticmethod
    def find_window(title_partial: str) -> Optional['WindowEnumerator.WindowInfo']:
        """Find a window by partial title match."""
        for w in WindowEnumerator.list_windows():
            if title_partial.lower() in w.title.lower():
                return w
        return None

    @staticmethod
    def focus_window(hwnd: int):
        """Bring a window to the foreground."""
        user32.SetForegroundWindow(hwnd)

    @staticmethod
    def get_active_window() -> Optional['WindowEnumerator.WindowInfo']:
        """Get the currently focused window."""
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None

        title_buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, title_buf, 256)

        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))

        pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        class_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_buf, 256)

        return WindowEnumerator.WindowInfo(
            hwnd=hwnd,
            title=title_buf.value,
            class_name=class_buf.value,
            rect=(rect.left, rect.top, rect.right, rect.bottom),
            is_visible=True,
            pid=pid.value,
        )
