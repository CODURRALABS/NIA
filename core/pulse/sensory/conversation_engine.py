"""
ConversationEngine: Orchestrates real-time voice interaction for NIA.
Connects AudioEngine (streaming STT), LLMEngine (Reasoning), and VoiceEngine (streaming TTS).
"""
import logging
import asyncio
from typing import Callable
from sensory.audio_engine import AudioEngine
from sensory.voice_engine import VoiceEngine
from llm_engine import LLMEngine

logger = logging.getLogger("ConversationEngine")

class ConversationEngine:
    def __init__(self):
        self.audio = AudioEngine()
        self.voice = VoiceEngine()
        self.llm = LLMEngine()
        self.is_running = False
        self.chat_history = []
        
    async def start_session(self, on_transcript: Callable = None):
        """Starts a continuous real-time conversation loop."""
        self.is_running = True
        logger.info("Starting real-time conversation loop...")
        
        # In a real implementation, we'd use a more advanced async STT callback
        # For now, let's use the wake-word or direct audio capture
        self.audio.start()
        
        try:
            while self.is_running:
                woken, text = self.audio.get_and_clear_active_state()
                if woken and text:
                    logger.info(f"User said: {text}")
                    if on_transcript:
                        on_transcript(text)
                    
                    # 1. Reasoning
                    self.chat_history.append({"role": "user", "content": text})
                    response = self.llm.generate(text) # Should be streamed in final version
                    self.chat_history.append({"role": "assistant", "content": response})
                    
                    # 2. Speaking (Streaming-like non-blocking)
                    logger.info(f"NIA: {response}")
                    self.voice.speak(response)
                    
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Conversation loop error: {e}")
        finally:
            self.stop_session()

    def stop_session(self):
        self.is_running = False
        self.audio.stop()
        logger.info("Conversation session ended.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conv_engine = ConversationEngine()
    asyncio.run(conv_engine.start_session())
