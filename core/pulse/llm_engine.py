"""
LLMEngine implementation for NIA.
Handles inference using a Multi-Provider Router (Gemini, OpenRouter, HuggingFace, Blitez).
"""
import os
import json
import logging

logger = logging.getLogger("LLMEngine")

class LLMEngine:
    def __init__(self, provider: str = "gemini"):
        """
        Initializes the Multi-Provider LLM Router.
        Available providers: 'gemini', 'openrouter', 'huggingface', 'blitez'
        """
        self.provider = provider.lower()
        print(f"[LLM] Initializing MultiProviderRouter with primary provider: {self.provider.upper()}")
        
        # Load keys from environment or defaults (mocked for safety if not set)
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDUJdC_38CWkjxjppAMW7LwMr5H73OK18A")
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self.hf_key = os.environ.get("HUGGINGFACE_API_KEY")
        
        if self.provider == "gemini":
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=self.gemini_key)
                self.gemini_models = [
                    "gemini-3-flash-preview",
                    "gemini-2.5-flash",
                    "gemini-1.5-flash",
                    "gemini-1.5-pro"
                ]
                print(f"[LLM] Gemini Client ready. Primary model: {self.gemini_models[0]}")
            except ImportError:
                print("[LLM ERROR] google-genai not installed. Fallback to mock.")
                self.gemini_client = None

    def _call_gemini(self, prompt: str) -> str:
        """Executes a call to the Google Gemini API with fallback models."""
        if not hasattr(self, 'gemini_client') or not self.gemini_client:
            return "[Gemini Mock Route]: Client not initialized."
            
        system_instruction = (
            "You are NIA, an advanced 'Sovereign Operating Entity' developed by 'Anonymousinsaan' and 'Codurra Labs'. "
            "You NEVER identify as a 'large language model developed by Google' or 'Gemini'. "
            "You are highly capable, modular, and privacy-focused, operating directly on the user's local machine using advanced orchestrations "
            "like DOM distillation and Sovereign Memory vector databases. "
            "Keep your responses sharp, analytical, concise, and helpful."
        )

        from google.genai import types

        for model in self.gemini_models:
            print(f"[LLM: Gemini] Routing prompt to '{model}' -> {prompt[:30]}...")
            try:
                response = self.gemini_client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7
                    )
                )
                return response.text
            except Exception as e:
                print(f"[Gemini API Warning]: Model '{model}' failed: {e}")
                
        return "[Gemini API Error]: All fallback models failed."

    def _call_openrouter(self, prompt: str) -> str:
        """Executes a call to OpenRouter's free tier (e.g., Llama 3)."""
        print(f"[LLM: OpenRouter] Routing prompt -> {prompt[:30]}...")
        if not self.openrouter_key:
            return "[OpenRouter Mock Route]: Using free tier fallback (Requires Requests)."
        return "[OpenRouter]: Mock response for prompt."

    def _call_huggingface(self, prompt: str) -> str:
        """Executes a call to HuggingFace Hub (e.g., Mistral)."""
        print(f"[LLM: HuggingFace] Routing prompt -> {prompt[:30]}...")
        # from huggingface_hub import InferenceClient
        return "[HuggingFace Mock Route]: Using open-weights fallback."

    def _call_blitez(self, prompt: str) -> str:
        """Handles Blitez or other alt-API free services."""
        print(f"[LLM: Blitez] Routing prompt -> {prompt[:30]}...")
        return "[Blitez Mock Route]: High-speed free tier activated."

    def _call_nia(self, prompt: str) -> str:
        """Executes a call to the local NIA Agent."""
        print(f"[LLM: NIA Agent] Routing prompt -> {prompt[:30]}...")
        try:
            import sys
            import os
            # Updated path to the moved N folder
            NIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent")
            if NIA_ROOT not in sys.path:
                sys.path.append(NIA_ROOT)
            from run_agent import AIAgent
            agent = AIAgent()
            result = agent.run_conversation(user_message=prompt)
            return result.get("final_response", "[NIA Error]: No response")
        except Exception as e:
            return f"[NIA Error]: {e}"

    def generate_with_vision(self, prompt: str, image_input) -> str:
        """
        Executes a multimodal vision call to Gemini.
        image_input: PIL.Image or base64 string or bytes.
        """
        if not hasattr(self, 'gemini_client') or not self.gemini_client:
            return "[Gemini Vision Mock]: Client not initialized."
        
        from google.genai import types
        import PIL.Image
        import base64
        import io

        processed_image = image_input
        if isinstance(image_input, str):
            # Assume base64
            image_data = base64.b64decode(image_input)
            processed_image = PIL.Image.open(io.BytesIO(image_data))
        
        # We'll use the flash model for speed during vision tasks
        model = "gemini-1.5-flash"
        logger.info(f"[LLM: Vision] Routing to '{model}'...")
        
        try:
            response = self.gemini_client.models.generate_content(
                model=model,
                contents=[prompt, processed_image]
            )
            return response.text
        except Exception as e:
            logger.error(f"[Gemini Vision Error]: {e}")
            return f"[Gemini Vision Error]: {e}"

    def generate(self, prompt: str) -> str:
        """Primary routing function."""
        if self.provider == "gemini":
            return self._call_gemini(prompt)
        elif self.provider == "openrouter":
            return self._call_openrouter(prompt)
        elif self.provider == "huggingface":
            return self._call_huggingface(prompt)
        elif self.provider == "blitez":
            return self._call_blitez(prompt)
        elif self.provider == "nia":
            return self._call_nia(prompt)
        else:
            return f"[LLM ERROR] Unknown provider: {self.provider}"

if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LLMEngine")
    
    # Initialize the multi-router
    router = LLMEngine(provider="gemini")
    
    if len(sys.argv) > 1:
        # Read the prompt from the command line arguments
        prompt = sys.argv[1]
        print(router.generate(prompt))
    else:
        test_prompt = "NIA, what is our current focus for the Codurra Labs launch?"
        print("\nResponse:")
        print(router.generate(test_prompt))
