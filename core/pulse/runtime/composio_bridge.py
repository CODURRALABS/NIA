"""
NIA Composio Bridge — 200+ Tool Integrations
Connects NIA to Gmail, Slack, GitHub, Notion, Google Drive, and more.
Replaces the empty MCP bridge stub.
"""

import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ComposioBridge")


class ComposioToolBridge:
    """
    Gives NIA access to 200+ pre-authenticated toolkits via Composio.
    Supports: Gmail, Slack, GitHub, Notion, Google Drive, Jira, Linear, Calendar, etc.
    Requires: COMPOSIO_API_KEY env var.
    """

    def __init__(self):
        self.composio = None
        self.session = None
        self._initialized = False

    def initialize(self, user_id: str = "nia_sovereign") -> bool:
        """Initialize the Composio session."""
        if self._initialized:
            return True

        api_key = os.environ.get("COMPOSIO_API_KEY")
        if not api_key:
            logger.warning("COMPOSIO_API_KEY not set. Composio bridge unavailable.")
            return False

        try:
            from composio import Composio
            from composio_langchain import LangchainProvider

            self.composio = Composio(provider=LangchainProvider())
            self.session = self.composio.sessions.create(user_id=user_id)
            self._initialized = True
            logger.info(f"Composio session created for user '{user_id}'. 200+ tools available.")
            return True
        except ImportError:
            logger.error("composio not installed. Run: pip install composio composio-langchain")
            return False
        except Exception as e:
            logger.error(f"Composio initialization failed: {e}")
            return False

    def get_all_tools(self, user_id: str = "nia_sovereign", limit: int = 50) -> List[Any]:
        """Get all available Composio tools."""
        if not self._initialized and not self.initialize():
            return []

        try:
            return self.composio.tools.get(user_id=user_id, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get tools: {e}")
            return []

    def get_tools_for_app(self, app_name: str, user_id: str = "nia_sovereign") -> List[Any]:
        """Get tools filtered by app name (e.g., 'github', 'gmail', 'slack')."""
        if not self._initialized and not self.initialize():
            return []

        try:
            return self.composio.tools.get(user_id=user_id, search=app_name)
        except Exception as e:
            logger.error(f"Failed to get tools for {app_name}: {e}")
            return []

    def execute_tool(self, slug: str, arguments: Dict[str, Any], user_id: str = "nia_sovereign") -> Dict[str, Any]:
        """Execute a specific Composio tool by slug."""
        if not self._initialized and not self.initialize():
            return {"error": "Composio not initialized"}

        try:
            result = self.composio.tools.execute(slug=slug, arguments=arguments, user_id=user_id)
            logger.info(f"Composio tool '{slug}' executed successfully.")
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"error": str(e), "success": False}

    def get_tool_definitions(self, user_id: str = "nia_sovereign") -> List[Dict[str, str]]:
        """Get tool names and descriptions for LLM function calling."""
        tools = self.get_all_tools(user_id=user_id)
        return [
            {
                "name": getattr(t, "name", str(t)),
                "description": getattr(t, "description", "No description available")
            }
            for t in tools
        ]

    def list_available_apps(self, user_id: str = "nia_sovereign") -> List[str]:
        """List all available app integrations."""
        tools = self.get_all_tools(user_id=user_id)
        apps = set()
        for t in tools:
            name = str(t).lower()
            for app in ["gmail", "github", "slack", "notion", "google", "jira",
                        "linear", "asana", "trello", "calendar", "drive", "sheets",
                        "twitter", "linkedin", "discord", "telegram"]:
                if app in name:
                    apps.add(app)
        return sorted(apps)


_nia_composio = ComposioToolBridge()


def get_composio() -> ComposioToolBridge:
    """Get the singleton Composio bridge instance."""
    return _nia_composio
