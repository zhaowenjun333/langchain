from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
from .base import tool_registry


class SubmitLeaveTool:
    name = "submit_leave_request"
    description = "Submit an employee leave request to HR system"

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        user_id = kwargs.get("user_id")
        start = kwargs.get("start")
        end = kwargs.get("end")
        leave_type = kwargs.get("leave_type", "annual")
        reason = kwargs.get("reason", "")
        # Simulate API call
        request_id = f"LR-{int(datetime.utcnow().timestamp())}"
        return {
            "ok": True,
            "request_id": request_id,
            "user_id": user_id,
            "start": start,
            "end": end,
            "leave_type": leave_type,
            "reason": reason,
            "status": "submitted",
        }


tool_registry.register(SubmitLeaveTool())