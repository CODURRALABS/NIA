"""
CodeAgent: Agent responsible for generating and executing code scripts.
"""
from llm_engine import LLMEngine
from agents.script_runner import ScriptRunner
import logging

logger = logging.getLogger("CodeAgent")

class CodeAgent:
    def __init__(self):
        self.llm = LLMEngine()
        self.runner = ScriptRunner()

    def generate_and_execute(self, task: str, language: str = "python"):
        """Generates code for a task and executes it immediately."""
        prompt = (
            f"Write a {language} script to: {task}\n"
            "Return ONLY the code, no markdown, no explanations."
        )
        code = self.llm.generate(prompt).strip()
        
        # Clean markdown if LLM ignored instructions
        if "```" in code:
            code = code.split("```")[1].split("\n", 1)[1].rsplit("```", 1)[0].strip()

        logger.info(f"Generated {language} code. Executing...")
        if language == "python":
            return self.runner.run_python(code)
        elif language == "powershell":
            return self.runner.run_powershell(code)
        else:
            return {"error": f"Unsupported language: {language}"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = CodeAgent()
    # Test: agent.generate_and_execute("print 'hello'")
