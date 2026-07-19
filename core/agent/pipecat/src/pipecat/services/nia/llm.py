#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import os
import sys
from typing import Any, List, Optional

from loguru import logger

from pipecat.frames.frames import (
    Frame,
    LLMContextFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
)
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.llm_service import LLMService

# Ensure NIA is in path
# The N folder is now inside the NIA root.
# This file is at: NIA/N/pipecat/src/pipecat/services/nia/llm.py
NIA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../"))
if NIA_ROOT not in sys.path:
    sys.path.append(NIA_ROOT)

try:
    from run_agent import AIAgent
except ImportError:
    logger.error("Could not import AIAgent from NIA. Ensure path is correct.")
    AIAgent = None

class NIALLMService(LLMService):
    """NIA LLM service for Pipecat.

    This service wraps the Nous NIA AIAgent and allows it to be used
    within a Pipecat pipeline.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if AIAgent:
            self._agent = AIAgent(
                # You can pass config overrides here
            )
        else:
            self._agent = None
            logger.error("NIA AIAgent not available.")

    async def _process_context(self, context: LLMContext):
        if not self._agent:
            await self.push_error("NIA AIAgent not initialized.")
            return

        # Convert Pipecat messages to NIA format
        # NIA uses standard OpenAI message format, which Pipecat's LLMContext also uses.
        messages = context.messages

        # AIAgent.run_conversation is synchronous, so we run it in a thread.
        # We'll use a simplified version for now. 
        # For full streaming support, we might need to hook into the agent's callback system.
        
        def run_nia():
            # Extract last user message
            user_msg = ""
            for msg in reversed(messages):
                if msg["role"] == "user":
                    user_msg = msg["content"]
                    break
            
            # We skip the history for now to keep it simple, or we can pass it
            history = messages[:-1] if len(messages) > 1 else []
            
            # Run the agent
            result = self._agent.run_conversation(user_message=user_msg, conversation_history=history)
            return result.get("final_response", "")

        response_text = await asyncio.to_thread(run_nia)
        
        if response_text:
            await self._push_llm_text(response_text)

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, LLMContextFrame):
            await self.push_frame(LLMFullResponseStartFrame())
            await self._process_context(frame.context)
            await self.push_frame(LLMFullResponseEndFrame())
        else:
            await self.push_frame(frame, direction)
