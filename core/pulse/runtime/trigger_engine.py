"""
NIA Hybrid Trigger Engine — Always-On Voice + Hotkey + API
Wires the VoiceEngine's always-listening microphone with the wake word
to the NIA process_task callback. Supports:
  - Wake word ("Nia, do X") via sounddevice + faster-whisper
  - CTRL+ALT+N hotkey via pynput
  - API trigger from FastAPI/WebHub
"""

import os
import time
import threading
import logging
from typing import Callable, Optional

logger = logging.getLogger("TriggerEngine")

try:
    from pynput import keyboard
except ImportError:
    keyboard = None


class HybridTriggerSystem:
    """
    NIA Hybrid Trigger Engine (WakeWord | Hotkey | API).
    Connects always-on microphone (VoiceEngine) to NIA's process_task.
    """
    def __init__(self, wake_word: str = "nia", on_trigger: Optional[Callable] = None):
        self.wake_word = wake_word.lower()
        self.on_trigger = on_trigger
        self.active = False
        self.mode = "hybrid"

        self._listening = False
        self._voice_engine = None
        self._stop_event = threading.Event()

        print(f"[TRIGGER]: Hybrid Engine initialized. Wake word: '{self.wake_word}'")

        if keyboard:
            try:
                self.hotkey_listener = keyboard.GlobalHotKeys({
                    '<ctrl>+<alt>+n': self._manual_trigger
                })
                self.hotkey_listener.start()
                print("[TRIGGER]: Manual Hotkey mapped: CTRL+ALT+N")
            except Exception as e:
                logger.warning("Failed to start hotkey listener: %s", e)

    def _manual_trigger(self):
        print("[TRIGGER]: Manual Hotkey Detect -> Igniting NIA.")
        if self.on_trigger:
            self.on_trigger(source="hotkey")

    def api_trigger(self):
        """Called by FastAPI PulseEngine when UI button is pressed."""
        print("[TRIGGER]: UI Button Signal -> Igniting NIA.")
        if self.on_trigger:
            self.on_trigger(source="api")

    def start_listening(self):
        """Start always-on microphone via VoiceEngine."""
        if self._listening:
            return

        try:
            from voice_engine import get_voice
            self._voice_engine = get_voice()
            if not self._voice_engine._stt_ready:
                self._voice_engine.initialize()

            self._voice_engine.start_always_listening(
                on_speech=self._handle_speech,
                wake_word=self.wake_word,
            )
            self._listening = True
            print(f"[TRIGGER]: Always-on listening active. Say '{self.wake_word}' + command.")
        except Exception as e:
            logger.warning("VoiceEngine always-on failed, falling back to hotkey-only: %s", e)
            print("[TRIGGER]: Microphone unavailable. Hotkey CTRL+ALT+N still works.")

    def _handle_speech(self, text: str):
        """Callback from VoiceEngine when speech is detected."""
        if self.on_trigger:
            self.on_trigger(source="voice", text=text)

    def stop(self):
        self._stop_event.set()
        if self._voice_engine:
            self._voice_engine.stop_listening()
        if hasattr(self, 'hotkey_listener'):
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
