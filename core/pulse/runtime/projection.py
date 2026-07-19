import re
import numpy as np

class SovereignProjection:
    """
    NIA Sovereign Projection Layer.
    Ensures linguistic fluidity and persona integrity.
    Prevents Chinese leaks and enforces the 'Guardian' identity.
    """
    def __init__(self, bridge=None):
        self.bridge = bridge
        self.persona_anchors = ["Boss", "NIA", "Sovereign", "Logic", "Guardian"]
        print("[PROJECTION]: Linguistic Projection Layer active. Persona: Guardian.")

    def project_response(self, text: str, sensory_data: list) -> str:
        """
        Projects a raw LLM response into the Sovereign space.
        Cleans up technical artifacts and enforces persona.
        """
        if not text:
            return "I am processing the math, Boss. Stand by."

        # 1. Strip internal thought tags
        clean_text = re.sub(r'\[INTERNAL_CRITIQUE\].*?\n', '', text, flags=re.DOTALL)
        clean_text = clean_text.replace("<|thought|>", "").replace("<|im_end|>", "").strip()

        # 2. Enforce Persona (Inject warmth if missing)
        if "Boss" not in clean_text and len(clean_text) > 20:
            clean_text = f"Boss, {clean_text}"

        return clean_text

    def apply_linguistic_filter(self, text: str) -> str:
        """
        THE LINGUISTIC GUARDIAN.
        Detects and removes non-English characters (specifically Chinese leaks).
        """
        # Detect Chinese characters
        if re.search(r'[\u4e00-\u9fff]', text):
            # If detected, strip them or provide a translation-styled apology
            # For now, we perform a hard-strip of non-latin/symbol characters
            text = re.sub(r'[^\x00-\x7F]+', '', text)
            text += "\n\n[PROJECTION_LOG]: I detected a non-sovereign token leak and have filtered it for you, Boss."
        
        return text

if __name__ == "__main__":
    proj = SovereignProjection()
    raw = "[INTERNAL_CRITIQUE]: Bad logic.\nHello world 你好"
    print(proj.apply_linguistic_filter(proj.project_response(raw, [])))
