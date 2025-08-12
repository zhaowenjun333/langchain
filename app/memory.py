from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime
from .mongo import get_collection

# In-memory fallbacks
_mem_history: Dict[str, List[Dict[str, Any]]] = {}
_mem_state: Dict[str, Dict[str, Any]] = {}


async def append_history(session_id: str, message: Dict[str, Any]) -> None:
    try:
        coll = get_collection("history")
        await coll.insert_one({"session_id": session_id, **message})
    except Exception:
        _mem_history.setdefault(session_id, []).append({"session_id": session_id, **message})


async def get_history(session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    try:
        coll = get_collection("history")
        cursor = coll.find({"session_id": session_id}).sort("timestamp", 1).limit(limit)
        return [doc async for doc in cursor]
    except Exception:
        items = _mem_history.get(session_id, [])
        return items[-limit:]


async def upsert_state(session_id: str, state: Dict[str, Any]) -> None:
    try:
        coll = get_collection("state")
        await coll.update_one({"session_id": session_id}, {"$set": state, "$setOnInsert": {"created_at": datetime.utcnow()}}, upsert=True)
    except Exception:
        _mem_state[session_id] = state | {"session_id": session_id, "updated_at": datetime.utcnow()}


async def get_state(session_id: str) -> Dict[str, Any] | None:
    try:
        coll = get_collection("state")
        doc = await coll.find_one({"session_id": session_id})
        if not doc:
            return None
        doc.pop("_id", None)
        return doc
    except Exception:
        return _mem_state.get(session_id)