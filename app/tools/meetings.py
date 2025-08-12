from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime
from .base import tool_registry


class SearchMeetingRoomsTool:
    name = "search_meeting_rooms"
    description = "Search available meeting rooms by capacity, time window, and location"

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        capacity = int(kwargs.get("capacity", 2))
        start = kwargs.get("start")
        end = kwargs.get("end")
        location = kwargs.get("location", "HQ")
        # Simulate inventory
        rooms: List[Dict[str, Any]] = [
            {"room_id": "R-101", "name": "Orion", "capacity": 8, "location": "HQ"},
            {"room_id": "R-201", "name": "Pegasus", "capacity": 12, "location": "HQ"},
            {"room_id": "R-301", "name": "Phoenix", "capacity": 16, "location": "HQ"},
        ]
        available = [r for r in rooms if r["capacity"] >= capacity and r["location"] == location]
        return {"ok": True, "rooms": available, "start": start, "end": end}


class BookMeetingRoomTool:
    name = "book_meeting_room"
    description = "Book a meeting room given room_id, start, end, and topic"

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        room_id = kwargs["room_id"]
        start = kwargs["start"]
        end = kwargs["end"]
        topic = kwargs.get("topic", "会议")
        booking_id = f"BK-{int(datetime.utcnow().timestamp())}"
        return {
            "ok": True,
            "booking_id": booking_id,
            "room_id": room_id,
            "start": start,
            "end": end,
            "topic": topic,
            "status": "confirmed",
        }


tool_registry.register(SearchMeetingRoomsTool())
tool_registry.register(BookMeetingRoomTool())