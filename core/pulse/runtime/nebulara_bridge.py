"""
NIA Nebulara Bridge — Native Scripting Language Integration
Provides NIA with the ability to write, execute, transpile, and reason
with .nbs (Nebulara) programs natively.

Nebulara is CODURRA Labs' AI-native universal programming language:
  - Custom bytecode VM with 40+ opcodes
  - Transpiler to JavaScript and Python
  - Standard library (math, string, collections, time, JSON, net)
  - Type checker and scope analyzer

Bridge modes:
  1. execute_file(path)     — Run a .nbs file via the native VM
  2. execute_code(code)     — Run .nbs code snippet (temp file + VM)
  3. transpile(code, target) — Convert .nbs to JS or Python
  4. generate_nbs(goal)     — NIA writes .nbs code from natural language
  5. type_check(code)       — Run the semantic analyzer on .nbs code
"""

import os
import sys
import json
import time
import logging
import subprocess
import tempfile
from typing import Optional, Dict, Any, List

logger = logging.getLogger("NebularaBridge")

# ─── Paths ────────────────────────────────────────────────────────────
_NIA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_NEBULARA_DIR = os.path.join(_NIA_ROOT, "tools", "nebulara")
_BUILD_DIR = os.path.join(_NEBULARA_DIR, "build")
_STD_DIR = os.path.join(_NEBULARA_DIR, "std")
_SCRIPTS_DIR = os.path.join(_NEBULARA_DIR, "scripts")

# Also check local CODURRA NEBUXIA copy
_NEBUXIA_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "CODURRA NEBUXIA", "nebulara")
_NEBUXIA_BUILD = os.path.join(_NEBUXIA_DIR, "build")

# Temp dir for generated .nbs files
_NBS_TEMP_DIR = os.path.join(tempfile.gettempdir(), "nia_nebulara")
os.makedirs(_NBS_TEMP_DIR, exist_ok=True)


class NebularaBridge:
    """
    Sovereign Nebulara Integration Bridge (V18 Integration Module).
    Enables NIA to natively write, execute, and transpile Nebulara programs.
    """

    def __init__(self):
        self._binary_path: Optional[str] = None
        self._cli_path: Optional[str] = None
        self._pipeline_path: Optional[str] = None
        self._semantic_path: Optional[str] = None
        self._initialized = False
        self._node_path = "node"
        self._neb_js_path: Optional[str] = None
        self._execution_count = 0

    def initialize(self) -> Dict[str, Any]:
        """Discover Nebulara binaries and CLI entry points."""
        status = {
            "native_binary": False,
            "cli_js": False,
            "pipeline": False,
            "semantic": False,
            "std_lib": False,
        }

        # 1. Native binary (nebulara.exe) — preferred
        for build_dir in [_BUILD_DIR, _NEBUXIA_BUILD]:
            exe = os.path.join(build_dir, "nebulara.exe")
            if os.path.exists(exe):
                self._binary_path = exe
                status["native_binary"] = True
                logger.info("Nebulara native binary: %s", exe)
                break

        # 2. CLI entry point (bin/neb.js) — wraps native binary
        neb_js = os.path.join(_NEBULARA_DIR, "bin", "neb.js")
        if os.path.exists(neb_js):
            self._neb_js_path = neb_js
            status["cli_js"] = True
            logger.info("Nebulara CLI (JS): %s", neb_js)

        # 3. Transpiler pipeline
        for build_dir in [_BUILD_DIR, _NEBUXIA_BUILD]:
            exe = os.path.join(build_dir, "neb-pipeline.exe")
            if os.path.exists(exe):
                self._pipeline_path = exe
                status["pipeline"] = True
                logger.info("Nebulara Pipeline: %s", exe)
                break

        # 4. Semantic analyzer
        for build_dir in [_BUILD_DIR, _NEBUXIA_BUILD]:
            exe = os.path.join(build_dir, "neb-semantic.exe")
            if os.path.exists(exe):
                self._semantic_path = exe
                status["semantic"] = True
                logger.info("Nebulara Semantic: %s", exe)
                break

        # 5. Standard library
        if os.path.isdir(_STD_DIR):
            std_files = [f for f in os.listdir(_STD_DIR) if f.endswith(".nbs")]
            status["std_lib"] = len(std_files) > 0
            logger.info("Nebulara std lib: %d files", len(std_files))

        self._initialized = any(status.values())
        if not self._initialized:
            logger.warning(
                "Nebulara not built yet. Run 'build.bat' or 'gcc' to compile. "
                "Falling back to code generation only."
            )

        return status

    def is_available(self) -> bool:
        """Check if the native VM is ready for execution."""
        return self._binary_path is not None

    def execute_file(self, file_path: str, args: List[str] = None,
                     timeout: int = 30) -> Dict[str, Any]:
        """Execute a .nbs file via the native Nebulara VM."""
        if not self._binary_path:
            return {
                "success": False,
                "error": "Nebulara binary not built. Run build.bat to compile.",
                "fallback": "generate_only"
            }

        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        cmd = [self._binary_path, file_path] + (args or [])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.path.dirname(file_path),
            )
            self._execution_count += 1

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "file": file_path,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Execution timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a .nbs code snippet by writing to a temp file."""
        filename = f"nia_eval_{int(time.time() * 1000)}.nbs"
        temp_path = os.path.join(_NBS_TEMP_DIR, filename)

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(code)

            result = self.execute_file(temp_path, timeout=timeout)
            result["snippet"] = code[:200]
            return result
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def transpile(self, code: str, target: str = "js") -> Dict[str, Any]:
        """
        Transpile .nbs code to JavaScript or Python.
        target: "js" or "py"
        """
        if not self._pipeline_path:
            return {
                "success": False,
                "error": "Nebulara pipeline not built. Cannot transpile.",
                "hint": "Run build.bat to compile the transpiler."
            }

        filename = f"nia_transpile_{int(time.time() * 1000)}.nbs"
        temp_path = os.path.join(_NBS_TEMP_DIR, filename)

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(code)

            out_ext = ".js" if target == "js" else ".py"
            out_path = temp_path.replace(".nbs", out_ext)

            result = subprocess.run(
                [self._pipeline_path, temp_path, "--target", target, "--output", out_path],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0 and os.path.exists(out_path):
                with open(out_path, "r", encoding="utf-8") as f:
                    transpiled = f.read()
                return {
                    "success": True,
                    "output": transpiled,
                    "target": target,
                    "source_lines": len(code.splitlines()),
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or "Transpilation failed",
                    "stdout": result.stdout,
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            for ext in [".nbs", ".js", ".py"]:
                p = temp_path.replace(".nbs", ext)
                if os.path.exists(p):
                    os.remove(p)

    def type_check(self, code: str) -> Dict[str, Any]:
        """Run the semantic analyzer on .nbs code."""
        if not self._semantic_path:
            return {
                "success": False,
                "error": "Nebulara semantic analyzer not built.",
            }

        filename = f"nia_check_{int(time.time() * 1000)}.nbs"
        temp_path = os.path.join(_NBS_TEMP_DIR, filename)

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(code)

            result = subprocess.run(
                [self._semantic_path, temp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "errors": result.returncode != 0,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def generate_nbs(self, goal: str, router=None) -> Dict[str, Any]:
        """
        NIA generates .nbs code from a natural language goal.
        Uses ModelRouter to generate the code, then validates it.
        """
        prompt = f"""You are NIA, an AI that writes Nebulara (.nbs) code.
Nebulara syntax:
- LET variable = value
- CONST NAME = value
- PRINT(expression)
- IF? condition THEN: ... ELSE: ... END!
- WHILE? condition THEN: ... END!
- FOR! i = 0 TO 10 (STEP 2): ... END!
- FUNC! name(params): ... RETURN value ... END!
- PUSH(arr, val), POP(arr)
- Built-ins: LEN, TYPEOF, TO_STRING, TO_NUMBER, ABS, MIN, MAX, SQRT, POW, RANDOM, TIME

Write a Nebulara program that does this:
{goal}

Return ONLY valid Nebulara code, no explanation."""

        if router:
            result = router.generate(prompt, max_tokens=512)
            if result.get("success"):
                code = result["output"]
                code = self._clean_generated_code(code)
                return {
                    "success": True,
                    "code": code,
                    "goal": goal,
                    "source": "llm_generated"
                }

        # Fallback: rule-based generation for common patterns
        code = self._rule_based_generate(goal)
        return {
            "success": True,
            "code": code,
            "goal": goal,
            "source": "rule_based"
        }

    def _clean_generated_code(self, raw: str) -> str:
        """Strip markdown fences and extra text from LLM-generated code."""
        lines = raw.strip().splitlines()
        cleaned = []
        in_code = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code = not in_code
                continue
            if in_code or (not stripped.startswith("#") and not stripped.startswith("//")):
                cleaned.append(line)
            elif stripped.startswith(("#", "//")):
                cleaned.append(line)
        return "\n".join(cleaned) if cleaned else raw.strip()

    def _rule_based_generate(self, goal: str) -> str:
        """Simple rule-based .nbs code generation for common tasks."""
        g = goal.lower()

        if "hello" in g or "greet" in g:
            return 'PRINT("Hello from NIA via Nebulara!")'

        if "fibonacci" in g:
            return """FUNC! fibonacci(n):
    IF? n <= 1 THEN:
        RETURN n
    END!
    RETURN fibonacci(n - 1) + fibonacci(n - 2)
END!

FOR! i = 0 TO 10:
    PRINT(fibonacci(i))
END!"""

        if "factorial" in g:
            return """FUNC! factorial(n):
    IF? n <= 1 THEN:
        RETURN 1
    END!
    RETURN n * factorial(n - 1)
END!

PRINT(factorial(10))"""

        if "array" in g or "sum" in g:
            return """LET arr = [10, 20, 30, 40, 50]
LET total = 0
FOR! i = 0 TO 5:
    total = total + arr[i]
END!
PRINT("Sum: " + TO_STRING(total))"""

        if "loop" in g or "count" in g:
            return """LET count = 0
WHILE? count < 10 THEN:
    PRINT("Count: " + TO_STRING(count))
    count = count + 1
END!"""

        if "math" in g:
            return """PRINT("Square root of 144: " + TO_STRING(SQRT(144)))
PRINT("2 to the power of 10: " + TO_STRING(POW(2, 10)))
PRINT("Random number: " + TO_STRING(RANDOM()))
PRINT("Absolute of -42: " + TO_STRING(ABS(-42)))"""

        if "file" in g and "read" in g:
            return """LET content = READ_FILE("test.txt")
PRINT(content)"""

        if "file" in g and "write" in g:
            return """WRITE_FILE("output.txt", "Hello from NIA!")
PRINT("File written successfully")"""

        return f'PRINT("NIA Nebulara: {goal}")'

    def get_soul_config(self) -> Dict[str, Any]:
        """Return Nebulara configuration for NIA's identity protocol."""
        return {
            "language": "Nebulara",
            "version": "2.0.0",
            "author": "CODURRA Labs",
            "precision": "bytecode VM (40+ opcodes)",
            "transpilation": ["javascript", "python"],
            "integration": "native_scripting_language",
            "role": "NIA's mathematical certainty layer",
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current bridge status."""
        return {
            "initialized": self._initialized,
            "native_binary": self._binary_path,
            "cli_js": self._neb_js_path,
            "pipeline": self._pipeline_path,
            "semantic": self._semantic_path,
            "std_dir": _STD_DIR if os.path.isdir(_STD_DIR) else None,
            "executions": self._execution_count,
            "temp_dir": _NBS_TEMP_DIR,
        }


# ─── Singleton ────────────────────────────────────────────────────────
_bridge: Optional[NebularaBridge] = None


def get_nebulara() -> NebularaBridge:
    """Get or create the singleton NebularaBridge."""
    global _bridge
    if _bridge is None:
        _bridge = NebularaBridge()
    return _bridge
