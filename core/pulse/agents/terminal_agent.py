"""
TerminalAgent: Executes shell commands (PowerShell/CMD) and returns output.
"""
import subprocess
import logging
import os

logger = logging.getLogger("TerminalAgent")

class TerminalAgent:
    def execute(self, command: str, shell: str = "powershell"):
        """Executes a command and returns stdout/stderr."""
        logger.info(f"Executing command via {shell}: {command}")
        
        try:
            # For powershell, we might need a specific execution policy or wrapper
            if shell == "powershell":
                final_command = ["powershell", "-Command", command]
            else:
                final_command = command
                
            result = subprocess.run(
                final_command,
                capture_output=True,
                text=True,
                shell=(shell != "powershell"),
                check=False
            )
            
            output = result.stdout if result.stdout else ""
            error = result.stderr if result.stderr else ""
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": output,
                "error": error,
                "code": result.returncode
            }
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {"status": "error", "message": str(e)}

    def run_script(self, script_path: str):
        """Runs a .ps1, .bat, or .py script."""
        ext = os.path.splitext(script_path)[1].lower()
        if ext == ".ps1":
            return self.execute(f"& '{script_path}'", shell="powershell")
        elif ext == ".bat" or ext == ".cmd":
            return self.execute(script_path, shell="cmd")
        elif ext == ".py":
            return self.execute(f"python '{script_path}'", shell="cmd")
        else:
            return {"status": "error", "message": f"Unsupported script type: {ext}"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = TerminalAgent()
    print(agent.execute("dir", shell="cmd")["output"][:500])
