from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator, Dict, Any
from datetime import datetime
import json

# Ensure tools register on import
from . import tools  # noqa: F401

from .models import ChatRequest, ChatMessage, GraphState
from .memory import append_history, get_history, upsert_state, get_state
from .graph import handle_user_message, handle_user_reply_to_questions

app = FastAPI(title="Multi-Agent Orchestrator")


@app.get("/health")
async def health():
    return {"ok": True, "time": datetime.utcnow().isoformat()}


async def _stream_events(gen):
    async for ev in gen:
        yield {
            "event": ev.get("type", "message"),
            "data": json.dumps(ev),
        }


async def orchestrate_stream(req: ChatRequest) -> AsyncGenerator[Dict[str, Any], None]:
    # Load state
    state_doc = await get_state(req.session_id)
    if state_doc:
        state = GraphState(**state_doc)
    else:
        state = GraphState(user_id=req.user_id, session_id=req.session_id)

    # Append user message
    user_msg = ChatMessage(role="user", content=req.message)
    state.messages.append(user_msg)
    await append_history(req.session_id, user_msg.model_dump())

    # If awaiting user input, treat message as answers
    if state.awaiting_user_input:
        yield {"type": "agent_start", "text": "processing_user_answers"}
        state = await handle_user_reply_to_questions(state, req.message)
    else:
        yield {"type": "agent_start", "text": "planning_and_execution"}
        state = await handle_user_message(state)

    # Persist
    await upsert_state(req.session_id, state.model_dump())
    # Append assistant messages to history
    for m in state.messages[::-1]:
        # append only the last agent messages for this turn
        if m.role == "agent" and m.timestamp >= user_msg.timestamp:
            await append_history(req.session_id, m.model_dump())

    # Stream the agent messages as a single chunk for simplicity
    agent_outputs = [m.content for m in state.messages if m.role == "agent" and m.timestamp >= user_msg.timestamp]
    if agent_outputs:
        yield {"type": "agent_message", "text": "\n".join(agent_outputs)}
    yield {"type": "final", "ok": True}


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def event_generator():
        async for event in orchestrate_stream(req):
            yield {"event": event.get("type", "message"), "data": json.dumps(event)}
    return EventSourceResponse(event_generator())


@app.post("/chat")
async def chat(req: ChatRequest):
    collected = []
    async for ev in orchestrate_stream(req):
        collected.append(ev)
    return JSONResponse({"events": collected})


@app.get("/sessions/{session_id}/history")
async def session_history(session_id: str):
    items = await get_history(session_id)
    for item in items:
        item.pop("_id", None)
    return {"history": items}