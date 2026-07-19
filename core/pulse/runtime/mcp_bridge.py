"""
NIA MCP Bridge — Model Context Protocol Server Integration
Wires Composio (200+ tools) as the backend for MCP-style tool calls.
Provides a unified interface for NIA to discover, call, and manage
external tools via both MCP and Composio protocols.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("MCPBridge")


class MCPBridge:
    """
    Sovereign MCP Bridge (V19).
    Wraps Composio as the tool backend, exposing MCP-compatible
    connect_server / fetch_resource / call_tool interface.
    """

    def __init__(self):
        self.connected_servers: List[str] = []
        self._composio = None
        logger.info("MCP Bridge initialized.")

    def _get_composio(self):
        """Lazy-load Composio bridge."""
        if self._composio is None:
            from composio_bridge import get_composio
            self._composio = get_composio()
            if not self._composio._initialized:
                self._composio.initialize()
        return self._composio

    def connect_server(self, server_url: str) -> Dict[str, Any]:
        """Register an MCP server (Composio acts as the universal server)."""
        if server_url in self.connected_servers:
            return {"status": "already_connected", "server": server_url}
        self.connected_servers.append(server_url)
        logger.info(f"MCP Server connected: {server_url}")

        composio = self._get_composio()
        if composio._initialized:
            apps = composio.list_available_apps()
            return {
                "status": "connected",
                "server": server_url,
                "composio_apps": apps,
                "tool_count": len(composio.get_all_tools()),
            }
        return {"status": "connected", "server": server_url, "composio": "unavailable"}

    def fetch_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Fetch data from an MCP resource via Composio tool execution."""
        composio = self._get_composio()

        parts = resource_uri.split("://", 1)
        if len(parts) == 2:
            scheme, path = parts
        else:
            scheme, path = "tool", resource_uri

        if scheme == "composio" or scheme == "tool":
            slug = path.split("/")[0]
            return composio.execute_tool(slug, {})

        return {"uri": resource_uri, "data": "Resource not found", "error": "unsupported_scheme"}

    def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool via Composio."""
        composio = self._get_composio()
        result = composio.execute_tool(tool_name, args)
        logger.info(f"MCP tool '{tool_name}' executed via Composio.")
        return result

    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools from Composio."""
        composio = self._get_composio()
        return composio.get_tool_definitions()

    def search_tools(self, query: str) -> List[Dict[str, str]]:
        """Search tools by app name or keyword."""
        composio = self._get_composio()
        tools = composio.get_tools_for_app(query)
        return [
            {
                "name": getattr(t, "name", str(t)),
                "description": getattr(t, "description", "No description"),
            }
            for t in tools
        ]
