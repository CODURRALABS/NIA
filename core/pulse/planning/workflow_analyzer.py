"""
WorkflowAnalyzer: The pattern recognition core for Phase 17.
Analyzes user interaction timelines to suggest automations (Skills).
"""
import logging
import json
from llm_engine import LLMEngine
from skills.skill_generator import SkillGenerator

logger = logging.getLogger("WorkflowAnalyzer")

class WorkflowAnalyzer:
    def __init__(self):
        self.llm = LLMEngine()
        self.skill_gen = SkillGenerator()

    def analyze_timeline(self, timeline: list) -> dict:
        """
        Feeds the interaction timeline to the LLM to identify patterns.
        Returns a suggested skill description if a pattern is found.
        """
        if not timeline:
            return {"suggested": False, "reason": "Timeline is empty."}

        logger.info(f"Analyzing timeline of {len(timeline)} events...")
        
        # Prepare a concise view of the timeline for the LLM
        timeline_str = json.dumps(timeline[-50:], indent=2) # Last 50 events
        
        prompt = (
            "You are NIA's workflow analyzer. Analyze the following user interaction timeline "
            "and determine if there is a repetitive or automatable pattern.\n\n"
            "Timeline:\n"
            f"{timeline_str}\n\n"
            "If you detect a pattern (e.g., clicking a specific sequence, repetitive typing), "
            "respond with a JSON object:\n"
            "{\n"
            "  'suggested': true,\n"
            "  'skill_name': 'short_descriptive_name',\n"
            "  'task_description': 'A detailed task description for the SkillGenerator',\n"
            "  'reason': 'Explanation of the detected pattern'\n"
            "}\n"
            "Otherwise, return {'suggested': false}."
        )

        response = self.llm.generate(prompt)
        
        # Clean JSON and parse
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(response)
            return analysis
        except Exception as e:
            logger.error(f"Failed to parse workflow analysis: {e}")
            return {"suggested": False, "reason": "LLM response parsing failed."}

    def synthesize_skill(self, analysis: dict) -> str:
        """Uses the SkillGenerator to create a skill from an analysis recommendation."""
        if not analysis.get("suggested"):
            return ""
            
        logger.info(f"Synthesizing suggested skill: {analysis['skill_name']}")
        task_desc = analysis.get("task_description", "")
        return self.skill_gen.generate_skill(task_desc)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = WorkflowAnalyzer()
    # Mock test
    test_timeline = [
        {"time": 1, "type": "click", "pos": (100, 200)},
        {"time": 2, "type": "click", "pos": (100, 200)},
        {"time": 3, "type": "click", "pos": (100, 200)},
    ]
    result = analyzer.analyze_timeline(test_timeline)
    print(f"Analysis Result: {result}")
