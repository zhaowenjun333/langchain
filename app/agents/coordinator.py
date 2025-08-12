from __future__ import annotations
from typing import Any, Dict, List
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from ..llm import get_chat_model


coordinator_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个调度智能体，负责把用户的一句话办公需求拆解为一个或多个任务。任务类型目前支持: leave(请假), meeting(预约会议室)。请输出JSON，字段 tasks: [{type, params}]. params 尽量从用户话语中提取，如开始时间、结束时间、人数、主题、地点、时长等。"),
    ("user", "{message}")
])


def build_coordinator() -> Runnable:
    model = get_chat_model(temperature=0.0)
    parser = JsonOutputParser()
    chain = coordinator_prompt | model | parser
    return chain


async def plan_tasks(message: str) -> List[Dict[str, Any]]:
    chain = build_coordinator()
    try:
        result = await chain.ainvoke({"message": message})
        tasks = result.get("tasks", [])
        # normalize
        normalized: List[Dict[str, Any]] = []
        for t in tasks:
            ttype = str(t.get("type", "")).lower()
            if ttype in {"leave", "meeting"}:
                normalized.append({"type": ttype, "params": t.get("params", {})})
        return normalized
    except Exception:
        # fallback heuristic
        tasks: List[Dict[str, Any]] = []
        if any(k in message for k in ["请假", "休假", "病假", "年假"]):
            tasks.append({"type": "leave", "params": {}})
        if any(k in message for k in ["会议室", "开会", "预约会议"]):
            tasks.append({"type": "meeting", "params": {}})
        if not tasks:
            tasks = [{"type": "meeting", "params": {}}]
        return tasks