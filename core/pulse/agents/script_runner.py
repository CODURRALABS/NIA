"""
ScriptRunner: Executes generated scripts in a controlled environment.
"""
import subprocess
import os
import logging
import tempfile

logger = logging.getLogger("ScriptRunner")

class ScriptRunner:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    def run_python(self, code: str):
        """Runs python code and returns output."""
        file_path = os.path.join(self.temp_dir, "nia_script.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return self._run_cmd(["python", file_path])

    def run_powershell(self, code: str):
        """Runs powershell code and returns output."""
        file_path = os.path.join(self.temp_dir, "nia_script.ps1")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
            
        return self._run_cmd(["powershell", "-ExecutionPolicy", "Bypass", "-File", file_path])

    def _run_cmd(self, cmd: list):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Script timed out."}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    runner = ScriptRunner()
    print(runner.run_python("print('Hello from ScriptRunner')"))
