from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system", "tool", "agent"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    meta: Dict[str, Any] = Field(default_factory=dict)


class WorkflowTask(BaseModel):
    type: Literal["leave", "meeting"]
    params: Dict[str, Any] = Field(default_factory=dict)


class GraphState(BaseModel):
    user_id: str
    session_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    slots: Dict[str, Any] = Field(default_factory=dict)
    task_queue: List[WorkflowTask] = Field(default_factory=list)
    pending_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    last_tool_result: Optional[Dict[str, Any]] = None
    route: Optional[str] = None
    awaiting_user_input: bool = False


class StreamEvent(BaseModel):
    type: Literal[
        "agent_start",
        "agent_message",
        "tool_call",
        "tool_result",
        "ask_user",
        "final",
        "error",
    ]
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)