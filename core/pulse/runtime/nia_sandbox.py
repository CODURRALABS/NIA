"""
NIA CUA Sandbox — Sandboxed Code Execution
Runs untrusted code in isolated VMs via CUA.
Safer than raw OS access for autonomous operation.
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("CUASandbox")


class NIAAgentSandbox:
    """
    Sandboxed execution environment for NIA.
    Runs code in isolated VMs (Linux/Windows/macOS) via CUA.
    Requires: cua pip package + CUA driver.
    """

    def __init__(self):
        self.sandbox = None
        self._initialized = False

    def initialize(self) -> bool:
        """Check if CUA is available."""
        if self._initialized:
            return True

        try:
            from cua import Sandbox
            self._initialized = True
            logger.info("CUA Sandbox available.")
            return True
        except ImportError:
            logger.warning("cua not installed. Run: pip install cua")
            return False

    async def spin_up(self, os_type: str = "linux") -> bool:
        """Start a new sandbox VM."""
        if not self._initialized and not self.initialize():
            return False

        try:
            from cua import Sandbox, Image

            image_map = {
                "linux": Image.linux(),
                "macos": Image.macos(),
                "windows": Image.windows()
            }

            self.sandbox = await Sandbox.ephemeral(image_map.get(os_type, Image.linux()))
            logger.info(f"CUA sandbox started: {os_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to start sandbox: {e}")
            return False

    async def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Execute code safely inside the sandbox.
        
        Args:
            code: Code to execute
            language: Language (python, bash, node, etc.)
        
        Returns:
            {"output": str, "screenshot": bytes, "success": bool}
        """
        if not self.sandbox:
            if not await self.spin_up():
                return {"error": "Sandbox not available", "success": False}

        try:
            if language == "python":
                result = await self.sandbox.shell.run(f"python3 -c '{code}'")
            elif language == "bash":
                result = await self.sandbox.shell.run(code)
            elif language == "node":
                result = await self.sandbox.shell.run(f"node -e '{code}'")
            else:
                result = await self.sandbox.shell.run(code)

            screenshot = await self.sandbox.screenshot()

            return {
                "output": str(result),
                "screenshot": screenshot,
                "success": True
            }
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return {"error": str(e), "success": False}

    async def run_script(self, script_path: str) -> Dict[str, Any]:
        """Upload and run a script file in the sandbox."""
        if not self.sandbox:
            if not await self.spin_up():
                return {"error": "Sandbox not available", "success": False}

        try:
            with open(script_path, "r") as f:
                code = f.read()

            result = await self.sandbox.shell.run(f"cat > /tmp/script.py << 'EOF'\n{code}\nEOF\npython3 /tmp/script.py")
            screenshot = await self.sandbox.screenshot()

            return {
                "output": str(result),
                "screenshot": screenshot,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def shutdown(self):
        """Shut down the sandbox."""
        if self.sandbox:
            try:
                await self.sandbox.close()
            except Exception:
                pass
            self.sandbox = None
            logger.info("CUA sandbox shut down.")


_nia_sandbox = NIAAgentSandbox()


def get_sandbox() -> NIAAgentSandbox:
    """Get the singleton CUA sandbox instance."""
    return _nia_sandbox
