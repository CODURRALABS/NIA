"""
NIA Kimi Code Bridge — Coding Agent via CLI
Spawns Kimi Code CLI as a subprocess for delegated coding tasks.
"""

import subprocess
import json
import logging
import os
import shutil
import time
import threading
from typing import Optional, Dict, Any

logger = logging.getLogger("KimiCodeBridge")


class KimiCodeBridge:
    """
    Delegates coding tasks to Kimi Code CLI via subprocess.
    Requires: Kimi Code CLI installed (irm https://code.kimi.com/kimi-code/install.ps1 | iex)
    """

    def __init__(self):
        self.proc = None
        self._available = None

    def is_available(self) -> bool:
        """Check if Kimi Code CLI is installed."""
        if self._available is not None:
            return self._available
        self._available = shutil.which("kimi") is not None
        if not self._available:
            logger.warning("Kimi Code CLI not found. Install via: irm https://code.kimi.com/kimi-code/install.ps1 | iex")
        return self._available

    def start_session(self) -> bool:
        """Start a Kimi Code ACP session."""
        if not self.is_available():
            return False

        if self.proc and self.proc.poll() is None:
            return True

        try:
            self.proc = subprocess.Popen(
                ["kimi", "acp"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            logger.info("Kimi Code ACP session started.")
            return True
        except Exception as e:
            logger.error(f"Failed to start Kimi Code: {e}")
            return False

    def delegate_coding_task(self, task_description: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Send a coding task to Kimi Code and wait for response.

        Args:
            task_description: Natural language coding task
            timeout: Max seconds to wait for response

        Returns:
            {"output": str, "success": bool}
        """
        if not self.start_session():
            return {"error": "Kimi Code not available", "success": False}

        try:
            task_payload = json.dumps({
                "type": "task",
                "input": task_description
            }) + "\n"

            self.proc.stdin.write(task_payload)
            self.proc.stdin.flush()

            output = ""
            result_event = threading.Event()
            result_data = {}

            def reader():
                nonlocal output
                try:
                    while result_event.is_set() is False:
                        line = self.proc.stdout.readline()
                        if not line:
                            break
                        output += line
                        try:
                            response = json.loads(line)
                            if response.get("type") == "result":
                                result_data["output"] = response.get("output", output)
                                result_data["success"] = True
                                result_event.set()
                                return
                        except json.JSONDecodeError:
                            continue
                except Exception:
                    pass
                result_event.set()

            t = threading.Thread(target=reader, daemon=True)
            t.start()
            result_event.wait(timeout=timeout)

            if result_data:
                return {"output": result_data.get("output", output), "success": True}
            return {"output": output.strip(), "success": bool(output)}
        except Exception as e:
            logger.error(f"Kimi Code task failed: {e}")
            return {"error": str(e), "success": False}

    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Execute a code snippet via Kimi Code."""
        task = f"Execute this {language} code and return the output:\n```{language}\n{code}\n```"
        return self.delegate_coding_task(task, timeout=60)

    def fix_code(self, file_path: str, error_message: str) -> Dict[str, Any]:
        """Ask Kimi Code to fix a bug in a file."""
        task = f"Fix the bug in {file_path}. Error: {error_message}"
        return self.delegate_coding_task(task, timeout=120)

    def refactor(self, file_path: str, instructions: str) -> Dict[str, Any]:
        """Ask Kimi Code to refactor code."""
        task = f"Refactor {file_path}: {instructions}"
        return self.delegate_coding_task(task, timeout=120)

    def shutdown(self):
        """Terminate the Kimi Code session."""
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            logger.info("Kimi Code session terminated.")


_nia_kimi = KimiCodeBridge()


def get_kimi() -> KimiCodeBridge:
    """Get the singleton Kimi Code bridge instance."""
    return _nia_kimi
