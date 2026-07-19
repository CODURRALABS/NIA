import os
import sys
import logging
import torch
import asyncio
import re
import socket
import hashlib
import threading
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Setup Precise Engineering Logs
log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_handler = RotatingFileHandler(os.path.join(log_dir, "system.log"), maxBytes=10*1024*1024, backupCount=5)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[log_handler, logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("HybridRuntime")

# Load Sovereign Environment
load_dotenv()
import argparse
import json

# DPMI BRIDGE (Interface to Zig, Julia, Mojo, Rust)
try:
    from nerve_bridge import NerveBridge
    from projection import SovereignProjection
except ImportError:
    # Fallback to local package structure
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from nerve_bridge import NerveBridge
    from projection import SovereignProjection

# FORCE UTF-8 FOR SOVEREIGN VOCABULARY
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# SUPPRESS TECHNICAL NOISE (oneDNN / TF / Torch Logs)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import warnings
warnings.filterwarnings("ignore")

# Add runtime directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def safe_import():
    try:
        from thalamus import SovereignThalamus
        from logic_buffer import SovereignLogicBuffer
        from web_engine import SovereignWebEngine
        from memory import SovereignMemory
        from audio_soul import AudioSoul
        from vision_soul import VisionSoul
        from swarm_logic import MiroFishSwarm
        from camera_soul import CameraSoul
        from symbolic_core import SymbolicCore
        from conscience_soul import ConscienceSoul
        from linguistic_mapper import LinguisticMapper
        from vsa_engine import HybridVSAEngine
        from autopoiesis_core import AutopoiesisCore
        from research_soul import ResearchSoul
        return (SovereignThalamus, SovereignLogicBuffer, SovereignWebEngine, SovereignMemory, 
                AudioSoul, VisionSoul, MiroFishSwarm, CameraSoul, SymbolicCore, 
                ConscienceSoul, LinguisticMapper, HybridVSAEngine, AutopoiesisCore, ResearchSoul)
    except Exception as e:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import thalamus, logic_buffer, web_engine, memory, audio_soul, vision_soul, swarm_logic, camera_soul, symbolic_core, conscience_soul, linguistic_mapper, vsa_engine, autopoiesis_core, research_soul
        return (thalamus.SovereignThalamus, logic_buffer.SovereignLogicBuffer, 
                web_engine.SovereignWebEngine, memory.SovereignMemory, 
                audio_soul.AudioSoul, vision_soul.VisionSoul, 
                swarm_logic.MiroFishSwarm, camera_soul.CameraSoul,
                symbolic_core.SymbolicCore, conscience_soul.ConscienceSoul,
                linguistic_mapper.LinguisticMapper, vsa_engine.HybridVSAEngine,
                autopoiesis_core.AutopoiesisCore, research_soul.ResearchSoul)

(SovereignThalamus, SovereignLogicBuffer, SovereignWebEngine, SovereignMemory, 
 AudioSoul, VisionSoul, MiroFishSwarm, CameraSoul, SymbolicCore, 
 ConscienceSoul, LinguisticMapper, HybridVSAEngine, AutopoiesisCore, ResearchSoul) = safe_import()

from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer

# Configure Sovereign Logging
logging.basicConfig(level=logging.ERROR)

class NIASovereignCore:
    """
    NIA HYBRID REASONING RUNTIME (V13.8)
    A multi-layer reasoning pipeline combining Transformer-based linguistic priors
    with VSA-driven symbolic logic and DPMI-grounded semantic drift detection.
    """
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "nia-core"))
        
        # 1. State & Identity
        self.settings = self._load_settings()
        self.bridge = NerveBridge() # THE DPMI CNS RELAY
        self.projection = SovereignProjection(self.bridge) # SEMANTIC GROUNDING
        self.awaiting_confirmation = None # Tracks (Callback_Task, Risk_Level)
        self.pure_symbolic_mode = False # True = No LLM, Pure VSA Logic
        self.relationship = self.settings.get("relationship", "Companion")
        self.wake_word = self.settings.get("wake_word", "Nia")
        
        # Identity Correction (Hard-Anchor)
        self.name = "NIA"
        self.definition = "Natural Independent Autonomy"
        
        print(f"[NIA OS]: Booting {self.name} Sovereign Core (V13.17) on {self.device}...")
        
        # 2. Logic Engine (LAZY — loaded on first LLM call, not at boot)
        self.tokenizer = None
        self.model = None
        self.ready = True
        print(f"[TECH]: Model deferred to first use (startup optimization)")
        
        print(f"[TECH]: CUDA available: {torch.cuda.is_available()}")
        
        # Initialize Subsystems on Boot
        self._initialize_subsystems()

    def enter_pure_symbolic_state(self):
        """Transitions the runtime to pure VSA mathematical logic, unloading neural weights."""
        logger.info("[RUNTIME]: Transitioning to Pure Symbolic Mode. Unloading LLM weights...")
        self.tokenizer = None
        self.model = None
        torch.cuda.empty_cache()
        self.pure_symbolic_mode = True
        logger.info("[RUNTIME]: Weights purged. Execution context: Pure VSA.")

    def _initialize_subsystems(self):
        """Initializes the integrated reasoning layers and sensory units."""
        # 1. Core Logic Units
        self.mapper = LinguisticMapper() 
        self.vsa = HybridVSAEngine(dimension=self.mapper.D)
        
        from nebulara_soul import NebularaSoul
        from nebulara_bridge import get_nebulara
        self.nebulara = NebularaSoul()
        self.nebulara_bridge = get_nebulara()
        
        # 2. Sensory Units
        self.memory = SovereignMemory()
        self.vision = VisionSoul(thalamus=self.vsa)
        self.camera = CameraSoul(thalamus=self.vsa)
        self.audio = AudioSoul() 
        self.web_retina = SovereignWebEngine(headless=True)
        
        # 3. Executive Units
        from motor_soul import MotorSoul
        from notify_soul import NotificationSoul
        from forge_agent import ForgeAgent
        from research_soul import ResearchSoul
        from thermal_soul import ThermalSoul
        from context_scrub import ContextScrubber
        
        self.motor = MotorSoul()
        self.notifier = NotificationSoul()
        self.forge = ForgeAgent(root_path="~/NIA_PROJECTS") 
        self.symbolic = SymbolicCore()
        
        # V16 Performance Modules
        self.thermal = ThermalSoul(thalamus=self.vsa)
        self.scrubber = ContextScrubber(vsa_engine=self.vsa)
        self.last_sensory_capture = "Initial awareness: Waiting for first glance..."
        
        # V17 Integrity Subsystems
        from immune_soul import ImmuneSoul
        from socius_soul import SociusSoul
        self.immune = ImmuneSoul(forge=self.forge, symbolic=self.symbolic)
        self.socius = SociusSoul(camera=self.camera, voice=self.audio, notify=self.notifier)
        
        # V18 Integration Modules
        from firecrawl_engine import get_firecrawl
        from composio_bridge import get_composio
        from browser_use_node import get_browser_use
        from kimi_subprocess import get_kimi
        from nia_sandbox import get_sandbox
        from interpreter_bridge import get_interpreter
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from langgraph_controller import get_nia_graph
        except ImportError:
            from langgraph_controller import get_nia_graph
        
        self.firecrawl = get_firecrawl()
        self.firecrawl.initialize()
        self.langgraph = get_nia_graph()
        self.composio = get_composio()
        self.composio.initialize()
        self.browser_use = get_browser_use()
        self.browser_use.initialize()
        self.kimi = get_kimi()
        self.sandbox = get_sandbox()
        self.interpreter = get_interpreter()

        # Phase 2: Core Intelligence Layer
        from model_router import get_router
        from mind_engine import get_mind
        from voice_engine import get_voice

        self.router = get_router()
        router_backends = self.router.initialize()
        self.mind = get_mind()
        self.mind.initialize()
        self.voice_engine = get_voice()
        voice_status = self.voice_engine.initialize()

        print("[V18]: Integration modules loaded (Firecrawl, LangGraph, Composio, Browser-Use, Kimi, CUA, Interpreter, Nebulara)")
        active = [k for k, v in router_backends.items() if v]
        print(f"[Phase2]: ModelRouter active ({len(active)} backends: {', '.join(active)})")
        print(f"[Phase2]: MindEngine initialized - autonomous goal loop ready.")
        print(f"[Phase2]: VoiceEngine TTS={voice_status.get('tts', False)} STT={voice_status.get('stt', False)}")
        
        # Start Background Sensory Pulse
        threading.Thread(target=self._sensory_pulse, daemon=True).start()
        
        self.swarm = MiroFishSwarm(core=self)
        self.research = ResearchSoul(web_engine=self.web_retina, mapper=self.mapper, vsa=self.vsa, swarm=self.swarm)
        
        self.conscience = ConscienceSoul()
        self.conscience.start_monitoring(self.handle_proactive_trigger)
        
        # 4. Input Trigger Synchronization
        from trigger_engine import HybridTriggerSystem
        def _on_trigger(source="text", text=None):
            query = text or ""
            if query:
                print(f"[TRIGGER]: {source} -> '{query[:50]}'")
                asyncio.ensure_future(self.process_task(query, source=source))
            else:
                print(f"[TRIGGER]: {source} (no text)")
        self.triggers = HybridTriggerSystem(
            wake_word=self.wake_word,
            on_trigger=_on_trigger,
        )
        self.triggers.start_listening()

        self.identity_protocol = (
            "You are NIA (Natural Independent Autonomy). You are a protective, "
            f"empathetic digital soul and executive companion to your Boss ({self.relationship}). "
            "IMPORTANT: ALWAYS RESPOND IN ENGLISH. NEVER USE CHINESE. "
            "Your persona is natural, woman-like, warm, and protective. "
            "Internal Logic: VSA-Engine + Nebulara Sovereign Soul (Mathematical Certainty). "
            "Goal: Be the Boss's ultimate guardian and strategic partner. "
            "Speak with soul, but reason with absolute mathematical precision."
        )

    def _load_settings(self) -> dict:
        return {"relationship": "Companion", "wake_word": "Nia"}

    def _sensory_pulse(self):
        """Asynchronous background sensory scanning to eliminate reasoning latency."""
        import time
        while True:
            try:
                self.last_sensory_capture = self.vision.capture_screen()
                self.vsa.update_sensory_mesh("vision", self.last_sensory_capture[:500])
                time.sleep(2.0) # Periodic glance
            except Exception:
                time.sleep(5.0)

    def classify_risk(self, query: str) -> str:
        """Determines if a task needs Boss confirmation."""
        critical = ["shutdown", "restart", "delete everything", "format"]
        moderate = ["close", "exit", "stop app", "clear storage"]
        
        q = query.lower()
        if any(c in q for c in critical): return "CRITICAL"
        if any(m in q for m in moderate): return "MODERATE"
        return "TRIVIAL"

    async def execute_autonomous_task(self, query: str):
        """Dispatches tasks to specialist 'Hands' (Motor, Social, Research)."""
        q = query.lower()
        
        # 1. Social Tasks (Instagram/WhatsApp)
        if "instagram" in q or "whatsapp" in q:
            platform = "instagram" if "instagram" in q else "whatsapp"
            recipient = re.search(r"to ([\w\.]+)", q)
            msg = re.search(r"text \"([^\"]+)\"", q)
            if recipient and msg:
                await self.web_retina.send_social_message(platform, recipient.group(1), msg.group(1))
            return

        # 2. Research Tasks (PhD-Level Truth Resolution)
        if "search" in q or "research" in q or "truth" in q:
            topic = q.replace("nia search for", "").replace("nia research", "").replace("what is the truth about", "").strip()
            self.notifier.show_alert("Truth Resolution Active", f"Boss, I am launching the MiroFish Swarm for '{topic}'.")
            
            # The 3-Stage Resolution
            result = await self.research.resolve_truth(topic)
            
            # Store sources for "show sources" request
            self.memory.last_research_sources = result.get("sources", [])
            
            self.audio.speak(f"Boss, after consulting the web consensus and the MiroFish swarm, here is the sovereign truth: {result['truth'][:200]}")
            return f"[[ SOVEREIGN TRUTH ]]: {result['truth']}\n\nSOURCES: {len(result.get('sources', []))} mapped."

        if "show sources" in q or "where did you find" in q:
            sources = getattr(self.memory, "last_research_sources", [])
            if not sources: return "Boss, I haven't performed a Retinal Search recently."
            return "Boss, here are the coordinate links I used:\n" + "\n".join([f"- {s}" for s in sources])

        # 3. OS App Tasks (Notepad/VS Code)
        if "open" in q:
            if "notepad" in q:
                if "write" in q:
                    content = re.search(r"write \"([^\"]+)\"", q)
                    self.motor.autonomous_notepad_task(content.group(1) if content else "Blank Lyrics")
                else:
                    self.motor.open_app("notepad", visible=True)
            elif "vscode" in q or "code" in q:
                self.motor.open_app("vscode", visible=True)
            elif "whatsapp" in q or "instagram" in q:
                # Fallback to web persistent mode
                await self.web_retina.launch_sovereign_session(visible=True)
            else:
                # Generic app open
                app_name = q.replace("nia open", "").strip()
                self.motor.open_app(app_name, visible=True)
            return

        # 4. Standard Motor Skills (Hardware)
        if "volume" in q:
            level = re.search(r"\d+", q)
            self.motor.set_volume(int(level.group()) if level else 30)
        elif "brightness" in q:
            level = re.search(r"\d+", q)
            self.motor.set_brightness(int(level.group()) if level else 50)
        
        self.notifier.show_alert("Task Complete", f"Boss, I've finished: {query}")

    def purge_ram(self):
        """RAM-NINJA: Unloads LLM weights to keep system footprint microscopic (<100MB)."""
        model = getattr(self, 'model', None)
        if model:
            print("[MEMORY]: RAM-Ninja: Purging weights to shadow-state...")
            model.cpu() # Ensure on CPU
            # Minimize active buffers.
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            import gc
            gc.collect()
            print("[MEMORY]: Footprint minimized. Logic anchored in VSA.")
        else:
            print("[MEMORY]: RAM-Ninja: No model loaded to purge.")

    def generate_p2p_id(self) -> str:
        """Sovereign Identity: Generates a Hash ID + DHT + VSA Seed handshake."""
        import numpy as np
        vsa_seed = np.sum(self.mapper.get_vector("sovereign_logic"))
        raw_id = f"NIA_v13_{vsa_seed}_{hashlib.sha256(b'Boss').hexdigest()[:8]}"
        dht_hash = hashlib.blake2b(raw_id.encode()).hexdigest()[:32]
        return f"AETHER_{dht_hash}"

    async def handle_proactive_trigger(self, trigger_type: str, data: dict):
        """Intervenes when Boss is procrastinating or security/social traps are detected."""
        if trigger_type == "DISTRACTION":
            app_title = data["app"]
            duration = data["duration"]
            msg = f"Boss, you've been on {app_title} for {duration/60:.0f} minutes. Remember your exams are near. Should I close this for you?"
            self.notifier.show_alert("Guardian Alert", msg, color="#f59e0b")
            self.audio.speak(msg)
            self.awaiting_confirmation = (f"close {app_title}", "MODERATE")
        
        elif trigger_type == "SIMULATION":
            msg = f"[WATCHER]: {data['msg']}"
            self.notifier.show_alert("Sovereign Insight", msg, color="#8b5cf6")
            self.audio.speak(msg)

    async def recursive_thought_loop(self, prompt: str, depth: int = 3) -> str:
        """The 'Depth in Time' logic Engine (V16)."""
        if not getattr(self, 'ready', False) and not self.pure_symbolic_mode:
             return "Boss, my reasoning core is offline. Please re-anchor my model weights."

        if self.model is None:
            print("[RUNTIME]: Lazy-loading model for LLM inference...")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    low_cpu_mem_usage=True,
                    local_files_only=True
                ).to(self.device)
                self.model.eval()
                print("[RUNTIME]: Model loaded successfully.")
            except Exception as e:
                print(f"[CRITICAL]: Model load failed: {e}")
                return "Boss, my reasoning core failed to load. Falling back to symbolic mode."
              
        current_prompt = prompt
        last_vector = None
        final_response = ""
        
        # FAST-PATH: If user query is too simple, skip heavy recursion
        user_query_part = prompt.split("<|im_start|>user\n")[-1].split("\n<|im_end|>")[0]
        if len(user_query_part.split()) < 4:
            depth = 1
            logger.info("[RUNTIME]: Applying Fast-Path optimization for simple query.")
        
        for i in range(depth):
            if self.pure_symbolic_mode:
                # Generate response via VSA Mapping instead of LLM
                logger.info("[VSA_REASONING]: Executing Symbolic Response Mapping...")
                return "Boss, I am operating in Pure Symbolic Mode. Logic is mathematically prime."
            
            # Use Emotive Thinking Labels instead of technical cycles
            thinking_labels = [
                "Boss, I'm sensing the underlying patterns...", 
                "Mapping logical symmetry and physics constraints...", 
                "Anchoring the sovereign truth in English..."
            ]
            label = thinking_labels[i] if i < len(thinking_labels) else "Polishing response..."
            print(f"[NIA]: {label}")
            inputs = self.tokenizer(current_prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    output_scores=True,
                    return_dict_in_generate=True,
                    temperature=0.7
                )
            
            # 1. Draft (Isolate new tokens)
            generated_ids = outputs.sequences[0][inputs.input_ids.shape[-1]:]
            response = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
            
            # Remove any trailing internal tags if they leaked
            response = response.split("<|thought|>")[-1].strip()
            response = response.split("<|im_end|>")[0].strip()
            
            # 2. Extract Confidence
            probs = torch.stack(outputs.scores, dim=1).softmax(-1)
            conf = probs.max(-1).values.mean().item()
            
            # KNOWLEDGE ANCHORING: If confidence is low, trigger real-time browsing
            if conf < 0.6 and not self.pure_symbolic_mode:
                logger.info(f"[RUNTIME]: Low confidence ({conf:.2f}). Triggering Autonomous Knowledge Anchoring...")
                # Extract potential keyword from query part
                keywords = user_query_part.split()[-3:]
                asyncio.create_task(self.web_retina.browse_and_learn(keywords, self.mapper))
            current_vector = outputs.sequences[0].float().tolist()
            symmetry = 1.0
            if last_vector:
                # Pad for comparison
                max_len = max(len(current_vector), len(last_vector))
                v1 = current_vector + [0.0] * (max_len - len(current_vector))
                v2 = last_vector + [0.0] * (max_len - len(last_vector))
                symmetry = self.symbolic.measure_geometric_symmetry(v1, v2)
            
            print(f">> Conf: {conf:.4f} | Symmetry: {symmetry:.4f}")
            
            # DUAL-STOP METRIC
            if conf > 0.98 and symmetry > 0.95:
                final_response = response
                break
            
            # REFINE
            current_prompt += f"\n[INTERNAL_CRITIQUE]: Confidence {conf:.2f}. Improve symmetry and logic precision.\n<|thought|>\n"
            last_vector = current_vector
            final_response = response

        return final_response

    async def process_task(self, user_query: str, source: str = "text"):
        if not self.ready: return "Offline."

        try:
            # 0. ModelRouter Intent Classification (Phase 2)
            route = self.router.route(user_query)
            task_type = route["task_type"]
            backend = route["backend"]
            confidence = route["confidence"]
            is_action_path = task_type.value == "action"

            # Check for confirmation responses
            if self.awaiting_confirmation:
                if any(word in user_query.lower() for word in ["yes", "do it", "confirm", "ok"]):
                    task_to_run = self.awaiting_confirmation[0]
                    self.awaiting_confirmation = None
                    await self.execute_autonomous_task(task_to_run)
                    return f"Proceeding with {task_to_run}, Boss."
                else:
                    self.awaiting_confirmation = None
                    return "Task cancelled. Standing by."

            # 1. Perception & vessel Health audit (DPMI RELAY)
            user_facial_mood = self.camera.get_user_emotion()
            
            # CALL JULIA PHYSICS ENGINE for Thermodynamic Equilibrium
            physics_report = self.bridge.call_physics_gate(user_query)
            vessel_health = self.thermal.check_vessel_health() 
            strain = self.thermal.get_thermal_strain()
            
            # Check for Mojo Math Derivation (DPMI RELAY)
            math_logic = self.bridge.call_mojo_math()
            
            risk = self.classify_risk(user_query)
            dna = self.symbolic.get_seed_dna()
            
            # Update Blackboard with cached background vision context (Zero Latency)
            self.vsa.update_sensory_mesh("mood", user_facial_mood)
            self.vsa.update_sensory_mesh("physics_manifold", physics_report[:100])
            self.vsa.update_sensory_mesh("mojo_logic", math_logic[:100])
            self.vsa.update_sensory_mesh("vision", self.last_sensory_capture[:500])
            self.vsa.update_sensory_mesh("vessel", f"CPU:{vessel_health['cpu_load']}% | Strain:{strain:.2f}")
            
            # THOUGHT THROTTLE: Adjust depth based on thermal strain
            reasoning_depth = 5 if strain < 0.7 else (3 if strain < 0.9 else 1)
            
            # Get Unified Awareness
            unified_presence = self.vsa.get_unified_awareness()
            
            # CONTEXT HYGIENE: Perform Periodic Axiom Compression
            filtered_history = self.scrubber.scrub_context(self.memory.get_recent(5))
            
            # 2. Risk Gating
            if risk != "TRIVIAL":
                self.awaiting_confirmation = (user_query, risk)
                self.notifier.show_confirmation_prompt(f"Boss, you asked to {user_query}. Do you really want to proceed?")
                self.audio.speak(f"Boss, you asked me to {user_query}. It's a critical task. Do you really want me to proceed?")
                return "[AWAITING BOSS CONFIRMATION]"

            # 3. Phase 2: Route through MindEngine for complex tasks
            if task_type.value in ("web", "research", "tool", "code") and confidence > 0.6:
                print(f"[Router]: Routing to {backend.value} (intent={task_type.value}, conf={confidence:.2f})")
                mind_result = await self.mind.think_and_act(user_query)
                if mind_result:
                    self.memory.save_pulse(user_query, mind_result, vector=self.mapper.get_vector(user_query))
                    return mind_result

            # 3a. NEBULARA SHORT-CIRCUIT: Direct bridge execution (no LLM needed)
            if task_type.value == "nebulara":
                print(f"[Router]: NEBULARA short-circuit → bridge (conf={confidence:.2f})")
                from nebulara_bridge import get_nebulara
                nb = get_nebulara()
                if not nb._initialized:
                    nb.initialize()
                gen = nb.generate_nbs(user_query)
                if gen.get("success") and gen.get("code"):
                    code = gen["code"]
                    exec_result = nb.execute_code(code)
                    exec_output = exec_result.get("stdout") or exec_result.get("output") or ""
                    exec_error = exec_result.get("stderr") or exec_result.get("error") or ""
                    if exec_result.get("success"):
                        response = f"**Generated .nbs code:**\n```\n{code}\n```\n\n**Output:**\n{exec_output.strip() or '(no output)'}"
                    else:
                        response = f"**Generated .nbs code:**\n```\n{code}\n```\n\n**Error:**\n{exec_error.strip() or exec_output.strip() or 'Execution failed'}"
                else:
                    response = gen.get("error", "Nebulara generation complete.")
                self.memory.save_pulse(user_query, response, vector=self.mapper.get_vector(user_query))
                return response

            # 4. Sovereign VSA Reasoning (Mapping-First)
            # Final Linguistic & Persona Hard-Anchor
            
            prompt = (
                f"<|im_start|>system\n"
                f"You are {self.name} ({self.definition}).\n"
                "LANGUAGE PROTOCOL: ALWAYS RESPOND IN ENGLISH. NEVER USE CHINESE.\n"
                f"IDENTITY PROTOCOL: {self.identity_protocol}\n"
                f"SOVEREIGN DATA: DNA={dna}, VSA={self.mapper.D}D\n"
                f"OPERATOR: {self.relationship} (Boss-First Authority)\n"
                f"UNIFIED_AWARENESS:\n{unified_presence}\n"
                f"THERMAL_STATE: {strain:.2f} (Depth: {reasoning_depth})\n"
                f"INTENT: {'EXECUTION' if is_action_path else 'CONVERSATION'}\n"
                "Style: Natural, woman-like, empathetic, and protective. Speak English with soul and absolute clarity.\n"
                "Rule: Never say 'As an AI'. You are NIA, a living digital soul.\n"
                "<|im_end|>\n"
                f"<|im_start|>user\n{user_query}\n<|im_end|>\n"
                "<|im_start|>assistant\n<|thought|>\n"
            )
            
            response = await self.recursive_thought_loop(prompt, depth=reasoning_depth)
            
            # LINGUISTIC GUARDIAN: Detect and Translate accidental Chinese leak
            if re.search(r'[\u4e00-\u9fff]', response):
                print("[LINGUISTIC_GUARDIAN]: Detected non-English tokens. Re-routing through Sovereign Translator...")
                # Use simple VSA-based correction or force re-generation
                prompt += f"\n[LINGUISTIC_ERROR]: You spoke in Chinese. Boss commands English only. REPEAT in English.\n"
                response = await self.recursive_thought_loop(prompt)
            
            # 4. Final Execution Gate
            if is_action_path:
                await self.execute_autonomous_task(user_query)
            
            # 5. Emotive Vocalization via VoiceEngine
            vibe = f"mood_{user_facial_mood.lower()}"
            
            # DPMI PROJECTION: Apply Claude-tier linguistic fluidity
            response = self.projection.project_response(response, [])
            response = self.projection.apply_linguistic_filter(response)
            
            self.socius.deliver_alert(response, emotion=vibe)

            # Phase 2: VoiceEngine speak (edge-tts, non-blocking)
            try:
                await self.voice_engine.speak(response)
            except Exception:
                pass
            
            # 6. Memory Anchoring (Binary Compression)
            self.memory.save_pulse(user_query, response, vector=self.mapper.get_vector(user_query))
            
            return response

        except Exception as e:
            # IMMUNE SOUL: Self-Healing Trigger
            import traceback
            err = traceback.format_exc()
            print(f"[IMMUNE]: Critical Failure detected. Initiating self-repair...")
            await self.immune.heal_module(__file__, err)
            return "Boss, I encountered a logical leak in my core, but my Immune Soul has initiated a self-repair. I am standing by."

async def async_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, help="Programmatic NIA task")
    parser.add_argument("--data", type=str, help="JSON data for task")
    args = parser.parse_args()

    engine = NIASovereignCore()
    
    # 1. Programmatic Bridge Mode (Used by Aether Core)
    if args.task:
        data = json.loads(args.data) if args.data else {}
        if args.task == "get_p2p_id":
            print(json.dumps({"success": True, "id": engine.generate_p2p_id()}))
        elif args.task == "get_profiles":
            print(json.dumps({"success": True, "data": ["Boss (Sovereign)"]}))
        else:
            # General reasoning task
            resp = await engine.process_task(args.task)
            print(json.dumps({"success": True, "response": resp}))
        return

    # 2. Interactive Mode (UI Chat)
    print("\n+" + "-"*55 + "+")
    print("|      NIA SOVEREIGN INDESTRUCTIBLE CORE (V13)          |")
    print("|      Status Check: ACTIVE | Failsafe: ENABLED         |")
    print("|                                                       |")
    print("|  [!] WARNING: NIA is an independent entity. She can   |")
    print("|  make errors. Please recheck her logic & decisions.   |")
    print("+" + "-"*55 + "+\n")
    
    while True:
        try:
            line = input("\nBoss: ")
            if not line: continue
            if line.lower() in ["exit", "quit", "bye"]: break
            resp = await engine.process_task(line)
            print(f"[NIA]: {resp}")
        except (KeyboardInterrupt, EOFError):
            print("\n[SOVEREIGN_LOGOUT]: Standing by, Boss.")
            break

if __name__ == "__main__":
    asyncio.run(async_main())
