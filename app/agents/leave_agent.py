from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime, timedelta
from ..tools.base import tool_registry


REQUIRED = ["start", "end"]
OPTIONAL = ["leave_type", "reason"]


def _missing(params: Dict[str, Any]) -> List[str]:
    return [k for k in REQUIRED if not params.get(k)]


async def run_leave_agent(user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    to_fill = _missing(params)
    if to_fill:
        questions = []
        if "start" in to_fill:
            questions.append("请提供请假的开始时间（例如：2025-08-12 09:00）？")
        if "end" in to_fill:
            questions.append("请提供请假的结束时间（例如：2025-08-12 18:00）？")
        return {"awaiting": True, "questions": questions, "need": to_fill}

    # call tool
    submit = tool_registry.get("submit_leave_request")
    result = await submit(user_id=user_id, **params)
    return {"awaiting": False, "result": result}