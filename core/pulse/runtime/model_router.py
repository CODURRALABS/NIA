"""
NIA Multi-Model Router — Intelligent Task Routing
Classifies user intent and routes to the best available backend:
  - HF Inference API (free tier, HF_TOKEN)
  - Local model (fallback, models/nia-core)
  - V18 modules (Firecrawl, Browser-Use, Composio, Interpreter)
  - VSA symbolic reasoning (mathematical certainty, no LLM)
"""

import os
import re
import json
import time
import logging
import requests
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

logger = logging.getLogger("ModelRouter")


class TaskType(Enum):
    CHAT = "chat"
    VISION = "vision"
    CODE = "code"
    WEB = "web"
    ACTION = "action"
    RESEARCH = "research"
    TOOL = "tool"
    NEBULARA = "nebulara"
    UNKNOWN = "unknown"


class ModelBackend(Enum):
    HF_API = "hf_inference"
    LOCAL = "local_model"
    VSA = "vsa_symbolic"
    FIRECRAWL = "firecrawl"
    BROWSER_USE = "browser_use"
    COMPOSIO = "composio"
    INTERPRETER = "interpreter"
    LANGGRAPH = "langgraph"
    NEBULARA = "nebulara"
    FREE_PROVIDER = "free_provider"

FREE_PROVIDERS = [
    {
        "name": "iflow",
        "url": "https://api.iflow.cn/v1/chat/completions",
        "key_env": "IFLOW_API_KEY",
        "models": ["kimi-k2-thinking", "qwen3-coder-plus", "deepseek-r1", "kimi-k2"],
    },
    {
        "name": "qwen",
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "key_env": "QWEN_API_KEY",
        "models": ["qwen3-coder-plus", "qwen3-coder-flash", "qwen3-coder-next"],
    },
    {
        "name": "siliconflow",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "key_env": "SILICONFLOW_API_KEY",
        "models": ["Qwen/Qwen3-8B", "THUDM/GLM-4-9B-Chat", "meta-llama/Meta-Llama-3.1-8B-Instruct"],
    },
    {
        "name": "nvidia_nim",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "key_env": "NVIDIA_API_KEY",
        "models": ["nvidia/llama-3.1-nemotron-70b-instruct", "meta/llama-3.1-8b-instruct"],
    },
    {
        "name": "openrouter_free",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": "OPENROUTER_API_KEY",
        "models": ["mistralai/mistral-7b-instruct:free", "meta-llama/llama-3.1-8b-instruct:free"],
    },
]


INTENT_PATTERNS = {
    TaskType.VISION: [
        r"look at", r"what do you see", r"screenshot", r"describe (the )?screen",
        r"what('s| is) on (my )?screen", r"capture", r"glance", r"read this",
    ],
    TaskType.CODE: [
        r"write (a )?(python |javascript |java |c\+\+ |rust |go )?(code|script|function|class|program)",
        r"debug", r"fix (the )?bug",
        r"refactor", r"implement",
        r"create (a )?(function|class|file|script|module)",
        r"programming", r"code (this|it|that)",
        r"python (function|script|code|class)",
        r"(function|script|code|class) (for|to|that)",
    ],
    TaskType.WEB: [
        r"search", r"research", r"browse", r"scrape",
        r"what('s| is) the (latest|news|weather)", r"look up", r"find (on|in) the web",
        r"google", r"website", r"url",
    ],
    TaskType.ACTION: [
        r"open (app|notepad|vscode|chrome|browser)", r"click", r"type",
        r"press", r"volume", r"brightness", r"close", r"shutdown",
        r"restart", r"keyboard", r"mouse",
    ],
    TaskType.RESEARCH: [
        r"explain (how|why|what)", r"tell me about", r"what do you know about",
        r"deep (dive|research)", r"analyze", r"compare", r"review",
    ],
    TaskType.TOOL: [
        r"send (an? )?(email|message|slack)", r"create (a )?(task|ticket|issue)",
        r"schedule", r"calendar", r"notion", r"github", r"jira",
    ],
    TaskType.NEBULARA: [
        r"\.nbs\b", r"nebulara", r"neb ",
        r"run (the )?(nbs|nebulara|neb) (file|script|program)",
        r"write (a )?(nbs|nebulara|neb) (program|script|function|code)",
        r"execute (the )?(nbs|nebulara|neb)",
        r"transpile (to|into) (js|javascript|python|py)",
        r"compile (the )?(nbs|nebulara)",
    ],
}


class ModelRouter:
    """
    Routes tasks to the optimal backend based on intent classification.
    Supports: HF Inference API, local model, VSA symbolic, V18 modules.
    """

    def __init__(self):
        self._hf_token = os.environ.get("HF_TOKEN")
        self._hf_model_cache: Dict[str, str] = {}
        self._local_model = None
        self._local_tokenizer = None
        self._backends_available: Dict[ModelBackend, bool] = {}
        self._stats: Dict[str, int] = {"routed": 0, "fallback": 0, "errors": 0}

    def initialize(self) -> Dict[str, bool]:
        """Probe all backends and report availability."""
        backends = {}

        # Free providers (OpenAI-compatible)
        self._available_free = []
        for provider in FREE_PROVIDERS:
            api_key = os.environ.get(provider["key_env"], "")
            if api_key:
                self._available_free.append(provider)
                backends[f"free_{provider['name']}"] = True
                logger.info("Free provider %s: available (%d models)", provider["name"], len(provider["models"]))
            else:
                backends[f"free_{provider['name']}"] = False

        if self._available_free:
            self._backends_available[ModelBackend.FREE_PROVIDER] = True
            logger.info("Free providers: %d configured", len(self._available_free))
        else:
            self._backends_available[ModelBackend.FREE_PROVIDER] = False

        # HF Inference API
        if self._hf_token:
            try:
                resp = requests.get(
                    "https://huggingface.co/api/whoami-v2",
                    headers={"Authorization": f"Bearer {self._hf_token}"},
                    timeout=5
                )
                backends["hf_api"] = resp.status_code == 200
                self._backends_available[ModelBackend.HF_API] = backends["hf_api"]
                if backends["hf_api"]:
                    logger.info("HF Inference API: available")
            except Exception:
                backends["hf_api"] = False
                self._backends_available[ModelBackend.HF_API] = False
                logger.info("HF Inference API: unreachable")
        else:
            backends["hf_api"] = False

        # Local model
        model_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "models", "nia-core"
        ))
        backends["local_model"] = os.path.exists(model_path)
        self._backends_available[ModelBackend.LOCAL] = backends["local_model"]
        if backends["local_model"]:
            logger.info("Local model: found at %s", model_path)

        # V18 modules (check lazily)
        for backend_name in ["firecrawl", "browser_use", "composio", "interpreter", "langgraph"]:
            backends[backend_name] = True  # lazy init, assume available
            logger.info("V18 module %s: assumed available (lazy init)", backend_name)

        return backends

    def classify_intent(self, query: str) -> Tuple[TaskType, float]:
        """
        Classify user intent from query text.
        Returns (TaskType, confidence).
        """
        q = query.lower().strip()

        scores: Dict[TaskType, int] = {}
        for task_type, patterns in INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, q))
            if score > 0:
                scores[task_type] = score

        if not scores:
            return TaskType.CHAT, 0.5

        best_type = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = scores[best_type] / total if total > 0 else 0.5

        return best_type, confidence

    def route(self, query: str) -> Dict[str, Any]:
        """
        Route a query to the optimal backend.
        Returns: {
            "task_type": TaskType,
            "backend": ModelBackend,
            "confidence": float,
            "params": dict (backend-specific)
        }
        """
        task_type, confidence = self.classify_intent(query)
        self._stats["routed"] += 1

        if task_type == TaskType.VISION:
            return {
                "task_type": task_type,
                "backend": ModelBackend.LOCAL,
                "confidence": confidence,
                "params": {"action": "capture_and_describe", "query": query}
            }

        if task_type == TaskType.CODE:
            if self._backends_available.get(ModelBackend.INTERPRETER):
                return {
                    "task_type": task_type,
                    "backend": ModelBackend.INTERPRETER,
                    "confidence": confidence,
                    "params": {"action": "execute_code", "query": query}
                }
            return {
                "task_type": task_type,
                "backend": ModelBackend.HF_API if self._backends_available.get(ModelBackend.HF_API) else ModelBackend.LOCAL,
                "confidence": confidence,
                "params": {"action": "generate_code", "query": query}
            }

        if task_type == TaskType.WEB:
            if self._backends_available.get(ModelBackend.FIRECRAWL):
                return {
                    "task_type": task_type,
                    "backend": ModelBackend.FIRECRAWL,
                    "confidence": confidence,
                    "params": {"action": "search_or_scrape", "query": query}
                }
            return {
                "task_type": task_type,
                "backend": ModelBackend.HF_API if self._backends_available.get(ModelBackend.HF_API) else ModelBackend.LOCAL,
                "confidence": confidence,
                "params": {"action": "research", "query": query}
            }

        if task_type == TaskType.ACTION:
            return {
                "task_type": task_type,
                "backend": ModelBackend.LOCAL,
                "confidence": confidence,
                "params": {"action": "execute_action", "query": query}
            }

        if task_type == TaskType.RESEARCH:
            return {
                "task_type": task_type,
                "backend": ModelBackend.HF_API if self._backends_available.get(ModelBackend.HF_API) else ModelBackend.LOCAL,
                "confidence": confidence,
                "params": {"action": "research", "query": query}
            }

        if task_type == TaskType.TOOL:
            return {
                "task_type": task_type,
                "backend": ModelBackend.COMPOSIO,
                "confidence": confidence,
                "params": {"action": "execute_tool", "query": query}
            }

        if task_type == TaskType.NEBULARA:
            return {
                "task_type": task_type,
                "backend": ModelBackend.NEBULARA,
                "confidence": confidence,
                "params": {"action": "execute_nebulara", "query": query}
            }

        # Default: chat via best available
        backend = ModelBackend.HF_API if self._backends_available.get(ModelBackend.HF_API) else ModelBackend.LOCAL
        return {
            "task_type": TaskType.CHAT,
            "backend": backend,
            "confidence": 0.5,
            "params": {"action": "chat", "query": query}
        }

    def generate_hf(self, prompt: str, model: str = None, max_tokens: int = 512,
                     temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate text via HF Inference API (free tier).
        Falls back to smaller models if rate-limited.
        """
        if not self._hf_token:
            return {"error": "HF_TOKEN not set", "success": False}

        # Model priority: best free models first
        models_to_try = [
            model,
            "mistralai/Mistral-7B-Instruct-v0.3",
            "HuggingFaceH4/zephyr-7b-beta",
            "microsoft/phi-2",
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        ]
        models_to_try = [m for m in models_to_try if m]

        first_error = None
        for m in models_to_try:
            try:
                resp = requests.post(
                    f"https://api-inference.huggingface.co/models/{m}",
                    headers={"Authorization": f"Bearer {self._hf_token}"},
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": max_tokens,
                            "temperature": temperature,
                            "return_full_text": False,
                        }
                    },
                    timeout=8
                )

                if resp.status_code == 200:
                    data = resp.json()
                    text = data[0].get("generated_text", "") if isinstance(data, list) else str(data)
                    logger.info("HF API success with model: %s", m)
                    self._backends_available[ModelBackend.HF_API] = True
                    return {"output": text.strip(), "model": m, "success": True}

                if resp.status_code == 503:
                    estimated_time = resp.json().get("estimated_time", 10)
                    if estimated_time < 15:
                        time.sleep(estimated_time + 1)
                        continue

                logger.warning("HF API %s returned %d", m, resp.status_code)

            except requests.Timeout:
                logger.warning("HF API timeout for model %s", m)
                if first_error is None:
                    first_error = "timeout"
                continue
            except requests.ConnectionError:
                logger.warning("HF API unreachable (DNS/network). Marking unavailable.")
                self._backends_available[ModelBackend.HF_API] = False
                return {"error": "HF API unreachable", "success": False}
            except Exception as e:
                err_str = str(e).lower()
                if "failed to resolve" in err_str or "nameResolutionError" in err_str:
                    logger.warning("HF API DNS resolution failed. Marking unavailable.")
                    self._backends_available[ModelBackend.HF_API] = False
                    return {"error": "HF API unreachable (DNS)", "success": False}
                logger.warning("HF API error for model %s: %s", m, e)
                continue

        self._backends_available[ModelBackend.HF_API] = False
        return {"error": "All HF models failed or rate-limited", "success": False}

    def generate_free(self, prompt: str, max_tokens: int = 512,
                       temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate text via free OpenAI-compatible providers (iFlow, Qwen, SiliconFlow, NVIDIA NIM, OpenRouter).
        Tries each provider's models in order until one succeeds.
        """
        for provider in self._available_free:
            api_key = os.environ.get(provider["key_env"], "")
            if not api_key:
                continue

            for model in provider["models"]:
                try:
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    }
                    resp = requests.post(
                        provider["url"],
                        headers=headers,
                        json=payload,
                        timeout=15,
                    )

                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["choices"][0]["message"]["content"]
                        logger.info("Free provider %s/%s success", provider["name"], model)
                        return {"output": text.strip(), "model": f"{provider['name']}/{model}", "success": True}

                    logger.warning("Free provider %s/%s returned %d", provider["name"], model, resp.status_code)

                except requests.Timeout:
                    logger.warning("Free provider %s/%s timeout", provider["name"], model)
                    continue
                except requests.ConnectionError:
                    logger.warning("Free provider %s unreachable", provider["name"])
                    break
                except Exception as e:
                    logger.warning("Free provider %s/%s error: %s", provider["name"], model, e)
                    continue

        return {"error": "All free providers failed", "success": False}

    def generate_local(self, prompt: str, max_tokens: int = 256) -> Dict[str, Any]:
        """Generate text via local model (lazy-loaded)."""
        import torch

        model_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "models", "nia-core"
        ))

        if not os.path.exists(model_path):
            return {"error": "Local model not found", "success": False}

        try:
            if self._local_model is None:
                from transformers import AutoTokenizer, AutoModelForCausalLM
                logger.info("Loading local model from %s...", model_path)
                self._local_tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
                self._local_model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    local_files_only=True
                )
                self._local_model.eval()
                logger.info("Local model loaded.")

            inputs = self._local_tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = self._local_model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    do_sample=True,
                )

            generated = outputs[0][inputs.input_ids.shape[-1]:]
            text = self._local_tokenizer.decode(generated, skip_special_tokens=True).strip()
            return {"output": text, "model": "local-nia-core", "success": True}

        except Exception as e:
            logger.error("Local model error: %s", e)
            return {"error": str(e), "success": False}

    def generate(self, prompt: str, backend: ModelBackend = None, **kwargs) -> Dict[str, Any]:
        """
        High-level generate: picks the best backend if not specified.
        Falls back: Free providers -> HF API -> local model.
        """
        if backend is None:
            if self._backends_available.get(ModelBackend.FREE_PROVIDER):
                backend = ModelBackend.FREE_PROVIDER
            elif self._backends_available.get(ModelBackend.HF_API):
                backend = ModelBackend.HF_API
            elif self._backends_available.get(ModelBackend.LOCAL):
                backend = ModelBackend.LOCAL
            else:
                return {"error": "No backends available", "success": False}

        if backend == ModelBackend.FREE_PROVIDER:
            result = self.generate_free(prompt, **kwargs)
            if not result.get("success"):
                logger.info("Free providers failed, trying HF API...")
                self._stats["fallback"] += 1
                if self._backends_available.get(ModelBackend.HF_API):
                    return self.generate_hf(prompt, **kwargs)
                return self.generate_local(prompt, max_tokens=kwargs.get("max_tokens", 256))
            return result
        elif backend == ModelBackend.HF_API:
            result = self.generate_hf(prompt, **kwargs)
            if not result.get("success"):
                logger.info("HF API failed, falling back to local model.")
                self._stats["fallback"] += 1
                return self.generate_local(prompt, max_tokens=kwargs.get("max_tokens", 256))
            return result
        elif backend == ModelBackend.LOCAL:
            return self.generate_local(prompt, **kwargs)
        else:
            return {"error": f"Backend {backend} not a text generator", "success": False}

    def unload_local(self):
        """Free local model memory."""
        import torch
        import gc
        if self._local_model is not None:
            del self._local_model
            del self._local_tokenizer
            self._local_model = None
            self._local_tokenizer = None
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            gc.collect()
            logger.info("Local model unloaded from memory.")

    def get_stats(self) -> Dict[str, int]:
        return dict(self._stats)


_nia_router = ModelRouter()


def get_router() -> ModelRouter:
    """Get the singleton ModelRouter instance."""
    return _nia_router
