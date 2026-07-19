"""
NIA Nebulara Soul — Sovereign Identity & Scripting Integration
Bridges NIA's core identity with the Nebulara programming language.
Delegates execution to NebularaBridge for actual VM operations.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger("NebularaSoul")


class NebularaSoul:
    """
    Sovereign Nebulara Soul (V18 Integration).
    Provides NIA with Nebulara as its native scripting language.
    Delegates heavy lifting to NebularaBridge.
    """

    def __init__(self):
        from nebulara_bridge import get_nebulara
        self._bridge = get_nebulara()
        status = self._bridge.initialize()
        self.ready = self._bridge._initialized
        logger.info("NebularaSoul initialized. Bridge status: %s", status)

    def run_script(self, script_path: str) -> Dict[str, Any]:
        """Execute a .nbs file via the Nebulara VM."""
        return self._bridge.execute_file(script_path)

    def execute_snippet(self, code: str) -> Dict[str, Any]:
        """Execute a .nbs code snippet."""
        return self._bridge.execute_code(code)

    def generate_and_run(self, goal: str) -> Dict[str, Any]:
        """NIA generates .nbs code from natural language, then executes it."""
        gen = self._bridge.generate_nbs(goal)
        if not gen.get("success"):
            return gen

        code = gen["code"]
        exec_result = self._bridge.execute_code(code)
        exec_result["generated_code"] = code
        exec_result["goal"] = goal
        return exec_result

    def transpile_to_js(self, code: str) -> Dict[str, Any]:
        """Transpile .nbs code to JavaScript."""
        return self._bridge.transpile(code, target="js")

    def transpile_to_python(self, code: str) -> Dict[str, Any]:
        """Transpile .nbs code to Python."""
        return self._bridge.transpile(code, target="py")

    def get_status(self) -> Dict[str, Any]:
        """Get bridge and soul status."""
        return {
            "soul_ready": self.ready,
            "bridge": self._bridge.get_status(),
            "identity": self._bridge.get_soul_config(),
        }


if __name__ == "__main__":
    soul = NebularaSoul()
    print(f"NebularaSoul ready: {soul.ready}")
    print(f"Status: {soul.get_status()}")
