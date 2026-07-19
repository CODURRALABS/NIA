"""
SkillGenerator: NIA's self-improvement core.
Handles autonomous Python code generation, execution, and debugging.
"""
import os
import subprocess
import logging
import time
from llm_engine import LLMEngine

logger = logging.getLogger("SkillGenerator")

class SkillGenerator:
    def __init__(self):
        self.llm = LLMEngine()
        self.skills_dir = os.path.join(os.path.dirname(__file__), "lib")
        os.makedirs(self.skills_dir, exist_ok=True)

    def generate_skill(self, task_description: str, retry_count: int = 2) -> str:
        """
        Prompts the LLM to write a Python script for a specific task.
        Attempts to execute and fix the script if it fails.
        """
        prompt = (
            f"Write a standalone Python script to accomplish the following task: {task_description}\n"
            "Requirements:\n"
            "1. The script must be executable with 'python script_name.py'.\n"
            "2. Only provide the Python code, no markdown formatting or extra text.\n"
            "3. Use standard libraries (os, sys, time, glob, etc.) or assume common NIA dependencies (requests, psutil, pillow).\n"
            "4. Include error handling and print meaningful output."
        )

        for attempt in range(retry_count + 1):
            logger.info(f"Generating skill for task: {task_description} (Attempt {attempt+1})")
            code = self.llm.generate(prompt)
            
            # Clean code block if LLM included them
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()

            filename = f"skill_{int(time.time())}.py"
            filepath = os.path.join(self.skills_dir, filename)

            with open(filepath, "w") as f:
                f.write(code)

            success, output, error = self.test_skill(filepath)
            
            if success:
                logger.info(f"Skill verified successfully: {filename}")
                return filepath
            else:
                logger.warning(f"Skill execution failed: {error}")
                prompt = (
                    f"The previously generated script failed with the following error:\n{error}\n"
                    f"Please fix the script and provide the corrected code for the task: {task_description}"
                )
        
        return ""

    def test_skill(self, filepath: str) -> tuple[bool, str, str]:
        """Runs the script and captures stdout/stderr."""
        try:
            result = subprocess.run(
                ["python", filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, result.stdout, ""
            else:
                return False, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Execution timed out (30s)."
        except Exception as e:
            return False, "", str(e)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generator = SkillGenerator()
    # Test generation
    path = generator.generate_skill("Create a text file named 'hello_nia.txt' with the current timestamp inside.")
    print(f"Generated Skill Path: {path}")
