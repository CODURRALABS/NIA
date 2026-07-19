"""
generate_samples.py: Generates 15s voice samples for Sarvam identities.
Saves to public/audio/samples/ for the Personalization page.
"""
import os
import sys
import time

# Add parent dir to path to import voice_engine
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from sensory.voice_engine import VoiceEngine

SAMPLE_TEXT = (
    "Hello. This is the {name} voice profile for NIA. "
    "I am your sovereign AI companion, designed to automate your workflows and provide intelligence at the edge. "
    "Testing audio fidelity and presence. All systems are nominal. Voice synchronization complete."
)

VOICES = [
    'meera', 'pavithra', 'mahesh', 'kumar', 
    'saranya', 'vignesh', 'mishti', 'arvind'
]

def generate():
    engine = VoiceEngine()
    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "public", "audio", "samples")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating samples in: {output_dir}")

    for v_id in VOICES:
        # For now, using local engine to simulate. 
        # In a production env, this might fetch from Sarvam directly.
        filename = os.path.join(output_dir, f"{v_id}.wav")
        text = SAMPLE_TEXT.format(name=v_id.capitalize())
        
        success = engine.save_to_file(text, filename)
        if success:
            print(f"Generated: {filename}")
        else:
            print(f"Failed: {v_id}")

if __name__ == "__main__":
    generate()
