"""
NIA Open Interpreter Bridge — Sandboxed Code Execution
Delegates untrusted code execution to Open Interpreter.
Supports both CLI binary and Python library fallback.
"""

import subprocess
import json
import logging
import os
import sys
import shutil
import time
import threading
from typing import Optional, Dict, Any

logger = logging.getLogger("InterpreterBridge")


class InterpreterBridge:
    """
    Delegates code execution to Open Interpreter.
    Tries CLI binary first, falls back to Python library (open-interpreter).
    Requires: interpreter CLI OR open-interpreter pip package.
    """

    def __init__(self):
        self.proc = None
        self._available = None
        self._use_library = False

    def is_available(self) -> bool:
        """Check if Open Interpreter is installed (CLI or library)."""
        if self._available is not None:
            return self._available

        if shutil.which("interpreter") is not None:
            self._available = True
            self._use_library = False
            logger.info("Open Interpreter CLI found.")
            return True

        try:
            import interpreter
            self._available = True
            self._use_library = True
            logger.info("Open Interpreter Python library found.")
            return True
        except ImportError:
            pass

        logger.warning("Open Interpreter not found. Install via: pip install open-interpreter")
        return False

    def start(self) -> bool:
        """Start an Open Interpreter ACP session."""
        if not self.is_available():
            return False

        if self._use_library:
            return True

        if self.proc and self.proc.poll() is None:
            return True

        try:
            self.proc = subprocess.Popen(
                ["interpreter", "acp"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            logger.info("Open Interpreter ACP session started.")
            return True
        except Exception as e:
            logger.error(f"Failed to start Open Interpreter: {e}")
            return False

    def execute_code_task(self, task: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Send a code execution task to Open Interpreter.

        Args:
            task: Natural language code task (e.g., "Calculate pi to 1000 digits")
            timeout: Max seconds to wait

        Returns:
            {"output": str, "success": bool}
        """
        if not self.start():
            return {"error": "Open Interpreter not available", "success": False}

        if self._use_library:
            return self._execute_via_library(task, timeout)

        return self._execute_via_cli(task, timeout)

    def _execute_via_library(self, task: str, timeout: int) -> Dict[str, Any]:
        """Execute via the Python library (open-interpreter)."""
        try:
            import interpreter
            interpreter.auto_run = True
            response = interpreter.chat(task)
            output = response.get("output", str(response)) if isinstance(response, dict) else str(response)
            return {"output": output, "success": True}
        except Exception as e:
            logger.error(f"Open Interpreter library execution failed: {e}")
            return {"error": str(e), "success": False}

    def _execute_via_cli(self, task: str, timeout: int) -> Dict[str, Any]:
        """Execute via CLI subprocess with threaded stdout reader."""
        try:
            task_payload = json.dumps({
                "type": "task",
                "input": task
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
            logger.error(f"Open Interpreter task failed: {e}")
            return {"error": str(e), "success": False}

    def run_python(self, code: str) -> Dict[str, Any]:
        """Execute Python code via Open Interpreter."""
        return self.execute_code_task(f"Execute this Python code:\n```python\n{code}\n```")

    def run_shell(self, command: str) -> Dict[str, Any]:
        """Execute a shell command via Open Interpreter."""
        return self.execute_code_task(f"Run this shell command: {command}")

    def shutdown(self):
        """Terminate the session."""
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            logger.info("Open Interpreter session terminated.")


_nia_interpreter = InterpreterBridge()


def get_interpreter() -> InterpreterBridge:
    """Get the singleton Interpreter bridge instance."""
    return _nia_interpreter
