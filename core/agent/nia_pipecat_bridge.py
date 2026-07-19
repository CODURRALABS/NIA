import asyncio
import os
import sys
from loguru import logger

# Add Pipecat and NIA to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "pipecat/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.services.nia.llm import NIALLMService
from pipecat.transports.local.audio import LocalAudioTransport
from pipecat.services.openai.tts import OpenAITTSService
from pipecat.services.openai.stt import OpenAIRealtimeSTTService

async def main():
    logger.info("Initializing NIA-Pipecat Sovereign Bridge...")

    # 1. Initialize NIA LLM Service (The Brain)
    nia = NIALLMService()

    # 2. Initialize Transport (Local Audio)
    transport = LocalAudioTransport()

    # 3. Initialize Services (Optional, using OpenAI for demo if keys exist)
    # In a fully sovereign setup, we'd use local Whisper and Piper.
    stt = None
    if os.environ.get("OPENAI_API_KEY"):
        stt = OpenAIRealtimeSTTService(api_key=os.environ["OPENAI_API_KEY"])
        tts = OpenAITTSService(api_key=os.environ["OPENAI_API_KEY"])
    else:
        logger.warning("OPENAI_API_KEY not found. Running in text-only pipeline mode for now.")
        stt = None
        tts = None

    # 4. Assemble Pipeline
    processors = [transport.input()]
    if stt: processors.append(stt)
    processors.append(nia)
    if tts: processors.append(tts)
    processors.append(transport.output())

    pipeline = Pipeline(processors)

    # 5. Create and Run Task
    task = PipelineTask(pipeline, PipelineParams(
        audio_out_sample_rate=24000,
    ))

    runner = PipelineRunner()
    
    logger.info("Bridge Active. Speak or type to interact with NIA through Pipecat.")
    await runner.run(task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bridge Shutdown.")
