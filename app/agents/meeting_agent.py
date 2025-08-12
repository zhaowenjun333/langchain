from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from ..tools.base import tool_registry


REQUIRED = ["start", "end", "attendees"]
OPTIONAL = ["topic", "location"]


def _missing(params: Dict[str, Any]) -> List[str]:
    missing = []
    for key in REQUIRED:
        if not params.get(key) and params.get(key) != 0:
            missing.append(key)
    return missing


async def run_meeting_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    to_fill = _missing(params)
    if to_fill:
        questions = []
        if "start" in to_fill:
            questions.append("请提供会议开始时间（例如：2025-08-12 10:00）？")
        if "end" in to_fill:
            questions.append("请提供会议结束时间（例如：2025-08-12 11:00）？")
        if "attendees" in to_fill:
            questions.append("请提供参会人数（例如：12）？")
        return {"awaiting": True, "questions": questions, "need": to_fill}

    capacity = int(params.get("attendees", 2))
    location = params.get("location", "HQ")
    topic = params.get("topic", "会议")

    search = tool_registry.get("search_meeting_rooms")
    sr = await search(capacity=capacity, start=params["start"], end=params["end"], location=location)
    if not sr.get("ok"):
        return {"awaiting": False, "error": "搜索会议室失败"}
    rooms = sr.get("rooms", [])
    if not rooms:
        return {"awaiting": False, "error": "没有满足条件的会议室"}

    # choose the smallest sufficient capacity
    chosen = sorted(rooms, key=lambda r: r["capacity"]) [0]

    book = tool_registry.get("book_meeting_room")
    br = await book(room_id=chosen["room_id"], start=params["start"], end=params["end"], topic=topic)
    return {"awaiting": False, "result": {"search": sr, "booking": br}}