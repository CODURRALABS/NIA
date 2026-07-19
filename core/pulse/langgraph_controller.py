"""
NIA LangGraph Controller — Orchestration State Machine
Replaces the manual orchestration loop with a proper StateGraph.
Routes tasks to the correct NIA module based on intent.
"""

import logging
from typing import TypedDict, Annotated, Optional, List, Any

logger = logging.getLogger("LangGraphController")


class NIAAgentState(TypedDict):
    user_input: str
    intent: str
    active_module: str
    results: List[str]
    final_response: str
    error: Optional[str]


def build_nia_controller_graph():
    """
    Build the NIA orchestration graph using LangGraph.
    
    Flow:
      START -> route -> [vision | action | web | code | chat] -> respond -> END
    
    The route node classifies intent and dispatches to the appropriate module.
    Each module processes the task and appends results.
    The respond node synthesizes the final response.
    """
    try:
        from langgraph.graph import StateGraph, START, END
    except ImportError:
        logger.error("langgraph not installed. Run: pip install langgraph")
        return None

    def route_intent(state: NIAAgentState) -> NIAAgentState:
        """Classify user intent and route to appropriate module."""
        query = state["user_input"].lower()

        if any(w in query for w in ["look at", "what do you see", "screenshot", "describe screen"]):
            state["active_module"] = "vision"
        elif any(w in query for w in ["click", "type", "open", "close", "volume", "brightness"]):
            state["active_module"] = "action"
        elif any(w in query for w in ["search", "research", "find", "browse", "scrape"]):
            state["active_module"] = "web"
        elif any(w in query for w in ["write code", "debug", "fix", "refactor", "implement"]):
            state["active_module"] = "code"
        else:
            state["active_module"] = "chat"

        state["intent"] = state["active_module"]
        return state

    def execute_vision(state: NIAAgentState) -> NIAAgentState:
        """Process vision/screenshot tasks."""
        try:
            from desktop_capture import DesktopCapture
            capture = DesktopCapture()
            frame = capture.grab()
            if frame:
                state["results"].append(f"Captured screen: {frame.width}x{frame.height}")
            else:
                state["results"].append("Screen capture failed")
        except Exception as e:
            state["error"] = f"Vision error: {e}"
        return state

    def execute_action(state: NIAAgentState) -> NIAAgentState:
        """Process hardware input actions."""
        try:
            from action_engine import ActionEngine
            engine = ActionEngine()
            result = engine.execute({
                "type": "focus",
                "params": {"title": state["user_input"]}
            })
            state["results"].append(f"Action result: {result}")
        except Exception as e:
            state["error"] = f"Action error: {e}"
        return state

    def execute_web(state: NIAAgentState) -> NIAAgentState:
        """Process web research/scraping tasks."""
        try:
            from firecrawl_engine import get_firecrawl
            fc = get_firecrawl()
            query = state["user_input"].replace("search for", "").replace("research", "").strip()
            results = fc.search_web(query, limit=3)
            state["results"].append(f"Found {len(results)} results for '{query}'")
            for r in results:
                state["results"].append(f"  - {r.get('title', 'untitled')}: {r.get('url', '')}")
        except Exception as e:
            state["error"] = f"Web error: {e}"
        return state

    def execute_code(state: NIAAgentState) -> NIAAgentState:
        """Process coding tasks via Kimi Code CLI."""
        try:
            from kimi_subprocess import KimiCodeBridge
            kimi = KimiCodeBridge()
            result = kimi.delegate_coding_task(state["user_input"])
            state["results"].append(f"Code result: {result}")
        except ImportError:
            state["results"].append("Kimi Code CLI not installed")
        except Exception as e:
            state["error"] = f"Code error: {e}"
        return state

    def execute_chat(state: NIAAgentState) -> NIAAgentState:
        """Process conversational tasks via local LLM."""
        state["results"].append(f"Chat response for: {state['user_input'][:50]}...")
        return state

    def respond(state: NIAAgentState) -> NIAAgentState:
        """Synthesize final response from all module results."""
        if state.get("error"):
            state["final_response"] = f"Error: {state['error']}"
        elif state["results"]:
            state["final_response"] = "\n".join(state["results"])
        else:
            state["final_response"] = "Task completed."
        return state

    graph = StateGraph(NIAAgentState)

    graph.add_node("route", route_intent)
    graph.add_node("vision", execute_vision)
    graph.add_node("action", execute_action)
    graph.add_node("web", execute_web)
    graph.add_node("code", execute_code)
    graph.add_node("chat", execute_chat)
    graph.add_node("respond", respond)

    graph.add_edge(START, "route")

    graph.add_conditional_edges(
        "route",
        lambda state: state["active_module"],
        {
            "vision": "vision",
            "action": "action",
            "web": "web",
            "code": "code",
            "chat": "chat",
        }
    )

    graph.add_edge("vision", "respond")
    graph.add_edge("action", "respond")
    graph.add_edge("web", "respond")
    graph.add_edge("code", "respond")
    graph.add_edge("chat", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


_graph_instance = None


def get_nia_graph():
    """Get or build the singleton NIA controller graph."""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = build_nia_controller_graph()
    return _graph_instance


async def execute_via_langgraph(user_input: str) -> str:
    """Execute a task through the LangGraph controller."""
    graph = get_nia_graph()
    if graph is None:
        return "LangGraph not available. Falling back to direct execution."

    initial_state: NIAAgentState = {
        "user_input": user_input,
        "intent": "",
        "active_module": "",
        "results": [],
        "final_response": "",
        "error": None
    }

    try:
        result = await graph.ainvoke(initial_state)
        return result.get("final_response", "No response generated.")
    except Exception as e:
        logger.error(f"LangGraph execution failed: {e}")
        return f"Execution error: {e}"
