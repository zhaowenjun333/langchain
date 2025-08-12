from __future__ import annotations
from typing import Any, Callable, Dict, Protocol


class Tool(Protocol):
    name: str
    description: str

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        ...


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def all(self) -> Dict[str, Tool]:
        return dict(self._tools)


tool_registry = ToolRegistry()


# Placeholder MCP tool adapter (implement for your MCP server)
class MCPTool:
    def __init__(self, name: str, description: str, mcp_command: str) -> None:
        self.name = name
        self.description = description
        self._mcp_command = mcp_command

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        # TODO: Implement actual MCP invocation according to your setup.
        # For now, echo input for demonstration.
        return {"ok": True, "tool": self.name, "called": self._mcp_command, "input": kwargs}