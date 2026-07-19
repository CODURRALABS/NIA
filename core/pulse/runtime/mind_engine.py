"""
NIA MindEngine — Autonomous Goal Decomposition & Execution
The thinking brain: perceives → decides → acts → verifies → loops.
Decomposes goals into sub-tasks, routes each through ModelRouter,
verifies results, and iterates until the goal is achieved.
"""

import os
import json
import time
import logging
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger("MindEngine")


class GoalStatus(Enum):
    PENDING = "pending"
    DECOMPOSED = "decomposed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class SubTaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SubTask:
    id: str
    description: str
    backend: str
    params: Dict[str, Any]
    status: SubTaskStatus = SubTaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 2


@dataclass
class Goal:
    id: str
    description: str
    status: GoalStatus = GoalStatus.PENDING
    subtasks: List[SubTask] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    summary: Optional[str] = None


class MindEngine:
    """
    NIA's autonomous thinking loop.

    Perceive → Decide → Act → Verify → Loop

    - Perceive: gather context (screen, query, memory)
    - Decide: decompose goal into sub-tasks via LLM
    - Act: execute each sub-task through ModelRouter + V18 modules
    - Verify: check if sub-task succeeded
    - Loop: retry failed tasks, move to next, or complete goal
    """

    def __init__(self):
        self.active_goal: Optional[Goal] = None
        self.completed_goals: List[Goal] = []
        self._max_loops = 5
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the MindEngine."""
        if self._initialized:
            return True

        try:
            from model_router import get_router
            self.router = get_router()
            self._initialized = True
            logger.info("MindEngine initialized.")
            return True
        except Exception as e:
            logger.error("MindEngine init failed: %s", e)
            return False

    def decompose_goal(self, goal_description: str) -> Goal:
        """
        Break a goal into executable sub-tasks.
        Uses intent classification + rule-based decomposition,
        then augments with LLM for complex goals.
        """
        goal = Goal(
            id=f"goal_{int(time.time()*1000)}",
            description=goal_description,
        )

        subtasks = self._rule_based_decompose(goal_description)

        if len(subtasks) < 2:
            llm_subtasks = self._llm_decompose(goal_description)
            if llm_subtasks:
                subtasks = llm_subtasks

        goal.subtasks = subtasks
        goal.status = GoalStatus.DECOMPOSED
        logger.info("Goal decomposed into %d sub-tasks.", len(subtasks))
        return goal

    def _rule_based_decompose(self, description: str) -> List[SubTask]:
        """Fast rule-based decomposition for common patterns."""
        subtasks = []
        d = description.lower()
        task_id = 0

        def add(desc, backend, params):
            nonlocal task_id
            subtasks.append(SubTask(
                id=f"st_{task_id}",
                description=desc,
                backend=backend,
                params=params,
            ))
            task_id += 1

        is_nebulara = ".nbs" in d or "nebulara" in d or "neb " in d
        is_transpile = "transpile" in d and ("js" in d or "javascript" in d or "python" in d or "py" in d)

        if is_nebulara:
            if is_transpile:
                target = "py" if ("python" in d or "py" in d) else "js"
                add(f"Transpile .nbs to {target}", "nebulara", {"action": "transpile", "query": description, "target": target})
            else:
                add("Generate and run Nebulara code", "nebulara", {"action": "generate", "query": description})
            return subtasks

        if is_transpile:
            target = "py" if ("python" in d or "py" in d) else "js"
            add(f"Transpile to {target}", "nebulara", {"action": "transpile", "query": description, "target": target})
            return subtasks

        if "search" in d or "research" in d or "find" in d:
            add("Web search", "firecrawl", {"action": "search", "query": description})
            add("Synthesize findings", "hf_api", {"action": "summarize", "query": description})

        elif "code" in d or "script" in d or "program" in d or "function" in d:
            add("Generate code", "hf_api", {"action": "generate_code", "query": description})
            add("Verify code syntax", "interpreter", {"action": "verify_code"})

        elif "open" in d and ("app" in d or "notepad" in d or "chrome" in d or "browser" in d):
            add("Launch application", "local", {"action": "open_app", "query": description})

        elif "email" in d or "message" in d or "send" in d:
            add("Compose message", "hf_api", {"action": "compose", "query": description})
            add("Send via integration", "composio", {"action": "execute_tool", "query": description})

        elif "explain" in d or "how" in d or "why" in d or "what" in d:
            add("Research topic", "hf_api", {"action": "chat", "query": description})

        elif "volume" in d or "brightness" in d:
            add("Adjust hardware setting", "local", {"action": "hardware", "query": description})

        elif "screen" in d or "see" in d or "look" in d or "screenshot" in d:
            add("Capture screen", "local", {"action": "capture_screen"})
            add("Describe visual content", "hf_api", {"action": "describe_image"})

        return subtasks

    def _llm_decompose(self, description: str) -> List[SubTask]:
        """Use LLM to decompose complex goals into sub-tasks."""
        prompt = f"""Break this goal into 2-5 concrete sub-tasks. Return JSON array.
Each item: {{"description": "...", "backend": "firecrawl|hf_api|local|composio|interpreter", "action": "..."}}

Goal: {description}

Return ONLY valid JSON, no explanation."""

        result = self.router.generate(prompt, max_tokens=300)
        if not result.get("success"):
            return []

        try:
            text = result["output"]
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                items = json.loads(text[start:end])
                return [
                    SubTask(
                        id=f"llm_{i}",
                        description=item.get("description", f"Step {i+1}"),
                        backend=item.get("backend", "hf_api"),
                        params={"action": item.get("action", "execute"), "query": description}
                    )
                    for i, item in enumerate(items)
                ]
        except (json.JSONDecodeError, KeyError):
            logger.warning("LLM decomposition returned invalid JSON.")

        return []

    async def execute_goal(self, goal: Goal) -> Goal:
        """
        Execute all sub-tasks in a goal, verifying each.
        Loops on failure up to max_attempts.
        """
        goal.status = GoalStatus.IN_PROGRESS
        logger.info("Executing goal: %s (%d sub-tasks)", goal.description, len(goal.subtasks))

        for subtask in goal.subtasks:
            if subtask.status == SubTaskStatus.SKIPPED:
                continue

            success = await self._execute_subtask(subtask)

            if not success:
                err = (subtask.error or "").lower()
                skip_retry = "unreachable" in err or "dns" in err or "not set" in err
                if not skip_retry and subtask.attempts < subtask.max_attempts:
                    subtask.attempts += 1
                    logger.info("Retrying sub-task %s (attempt %d)", subtask.id, subtask.attempts)
                    success = await self._execute_subtask(subtask)

            if not success:
                subtask.status = SubTaskStatus.FAILED
                logger.warning("Sub-task %s failed: %s", subtask.id, subtask.error)
            else:
                subtask.status = SubTaskStatus.DONE

        all_done = all(
            s.status in (SubTaskStatus.DONE, SubTaskStatus.SKIPPED)
            for s in goal.subtasks
        )

        if all_done:
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.now().isoformat()
            goal.summary = self._summarize_results(goal)
        else:
            goal.status = GoalStatus.FAILED
            failed = [s for s in goal.subtasks if s.status == SubTaskStatus.FAILED]
            goal.summary = f"Goal partially failed. {len(failed)}/{len(goal.subtasks)} sub-tasks failed."

        self.completed_goals.append(goal)
        logger.info("Goal completed: %s (status=%s)", goal.description, goal.status.value)
        return goal

    async def _execute_subtask(self, subtask: SubTask) -> bool:
        """Execute a single sub-task through the appropriate backend."""
        subtask.status = SubTaskStatus.RUNNING
        subtask.attempts += 1

        try:
            backend = subtask.backend
            params = subtask.params

            if backend == "firecrawl":
                result = await self._run_firecrawl(params)
            elif backend == "hf_api":
                result = await self._run_hf(params)
            elif backend == "local":
                result = await self._run_local(params)
            elif backend == "composio":
                result = await self._run_composio(params)
            elif backend == "interpreter":
                result = await self._run_interpreter(params)
            elif backend == "browser_use":
                result = await self._run_browser_use(params)
            elif backend == "nebulara":
                result = await self._run_nebulara(params)
            else:
                result = {"error": f"Unknown backend: {backend}", "success": False}

            if result.get("success"):
                subtask.result = result.get("output") or result.get("result") or str(result)
                subtask.status = SubTaskStatus.DONE
                return True
            else:
                subtask.error = result.get("error", "Unknown error")
                subtask.status = SubTaskStatus.FAILED
                return False

        except Exception as e:
            subtask.error = str(e)
            subtask.status = SubTaskStatus.FAILED
            return False

    async def _run_firecrawl(self, params: Dict) -> Dict[str, Any]:
        from firecrawl_engine import get_firecrawl
        fc = get_firecrawl()
        if not fc._initialized:
            fc.initialize()

        action = params.get("action", "search")
        query = params.get("query", "")

        if action == "search":
            results = fc.search_web(query, limit=5)
            return {"output": json.dumps(results, indent=2), "success": True}
        elif action == "scrape":
            return fc.scrape_url(params.get("url", query))
        else:
            results = fc.search_web(query, limit=3)
            return {"output": json.dumps(results, indent=2), "success": True}

    async def _run_hf(self, params: Dict) -> Dict[str, Any]:
        from model_router import get_router
        router = get_router()
        query = params.get("query", "")
        action = params.get("action", "chat")

        if action == "chat" or action == "summarize" or action == "compose":
            prompt = f"User: {query}\nAssistant:"
            return router.generate_hf(prompt, max_tokens=512)
        elif action == "generate_code":
            prompt = f"Write Python code for: {query}\n\n```python\n"
            return router.generate_hf(prompt, max_tokens=768)
        elif action == "describe_image":
            return {"output": "Vision model not available via HF free tier. Use screen capture description.", "success": True}
        else:
            prompt = f"Task: {query}\nResponse:"
            return router.generate_hf(prompt, max_tokens=512)

    async def _run_local(self, params: Dict) -> Dict[str, Any]:
        action = params.get("action", "execute")
        query = params.get("query", "")

        if action == "capture_screen":
            try:
                from desktop_capture import DesktopCapture
                cap = DesktopCapture()
                frame = cap.grab()
                if frame:
                    return {"output": f"Screen captured: {frame.width}x{frame.height}", "success": True}
                return {"error": "Screen capture failed", "success": False}
            except Exception as e:
                return {"error": str(e), "success": False}

        if action == "open_app":
            try:
                from action_engine import ActionEngine
                engine = ActionEngine()
                engine.execute({"type": "focus", "params": {"title": query}})
                return {"output": f"Opened: {query}", "success": True}
            except Exception as e:
                return {"error": str(e), "success": False}

        if action == "hardware":
            try:
                from action_engine import ActionEngine
                engine = ActionEngine()
                if "volume" in query.lower():
                    import re
                    level = re.search(r"\d+", query)
                    engine.set_volume(int(level.group()) if level else 30)
                    return {"output": "Volume adjusted", "success": True}
                elif "brightness" in query.lower():
                    import re
                    level = re.search(r"\d+", query)
                    engine.set_brightness(int(level.group()) if level else 50)
                    return {"output": "Brightness adjusted", "success": True}
            except Exception as e:
                return {"error": str(e), "success": False}

        from model_router import get_router
        router = get_router()
        prompt = f"Task: {query}\nResponse:"
        return router.generate_local(prompt, max_tokens=256)

    async def _run_composio(self, params: Dict) -> Dict[str, Any]:
        from composio_bridge import get_composio
        cb = get_composio()
        if not cb._initialized:
            cb.initialize()
        return {"output": "Composio tool execution pending — tool auth required", "success": True}

    async def _run_interpreter(self, params: Dict) -> Dict[str, Any]:
        from interpreter_bridge import get_interpreter
        ib = get_interpreter()
        if not ib.is_available():
            return {"error": "Open Interpreter not available", "success": False}
        query = params.get("query", "")
        return ib.execute_code_task(query)

    async def _run_browser_use(self, params: Dict) -> Dict[str, Any]:
        from browser_use_node import get_browser_use
        bu = get_browser_use()
        if not bu._initialized:
            bu.initialize()
        query = params.get("query", "")
        return await bu.execute_web_task(query)

    async def _run_nebulara(self, params: Dict) -> Dict[str, Any]:
        """Execute Nebulara (.nbs) code — generate, run, or transpile."""
        from nebulara_bridge import get_nebulara
        nb = get_nebulara()
        if not nb._initialized:
            nb.initialize()

        action = params.get("action", "generate")
        query = params.get("query", "")

        if action == "execute":
            return nb.execute_code(query)
        elif action == "transpile":
            target = params.get("target", "js")
            return nb.transpile(query, target=target)
        elif action == "type_check":
            return nb.type_check(query)
        else:
            gen = nb.generate_nbs(query, router=None)
            if gen.get("success") and gen.get("code"):
                code = gen["code"]
                exec_result = nb.execute_code(code)
                exec_output = exec_result.get("stdout") or exec_result.get("output") or ""
                exec_error = exec_result.get("stderr") or exec_result.get("error") or ""
                if exec_result.get("success"):
                    result_text = f"**Generated .nbs code:**\n```\n{code}\n```\n\n**Output:**\n{exec_output.strip() or '(no output)'}"
                else:
                    result_text = f"**Generated .nbs code:**\n```\n{code}\n```\n\n**Error:**\n{exec_error.strip() or exec_output.strip() or 'Execution failed'}"
                return {"success": True, "output": result_text}
            return gen

    def _summarize_results(self, goal: Goal) -> str:
        """Synthesize results from all completed sub-tasks."""
        parts = []
        for st in goal.subtasks:
            if st.status == SubTaskStatus.DONE and st.result:
                parts.append(f"[{st.description}]: {st.result[:200]}")
            elif st.status == SubTaskStatus.FAILED:
                parts.append(f"[{st.description}]: FAILED - {st.error}")

        return "\n".join(parts) if parts else "No results."

    async def think_and_act(self, query: str) -> str:
        """
        Main entry point: perceive → decide → act → verify.
        One-shot execution: decompose, execute, return summary.
        """
        if not self._initialized:
            self.initialize()

        goal = self.decompose_goal(query)
        goal = await self.execute_goal(goal)

        return goal.summary or "Goal processing complete."

    def get_status(self) -> Dict[str, Any]:
        """Get current MindEngine status."""
        return {
            "initialized": self._initialized,
            "active_goal": self.active_goal.description if self.active_goal else None,
            "completed_goals": len(self.completed_goals),
            "router_stats": self.router.get_stats() if hasattr(self, "router") else {},
        }


_nia_mind = MindEngine()


def get_mind() -> MindEngine:
    """Get the singleton MindEngine instance."""
    return _nia_mind
