from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime
from .models import GraphState, ChatMessage, WorkflowTask
from .agents.coordinator import plan_tasks
from .agents.leave_agent import run_leave_agent
from .agents.meeting_agent import run_meeting_agent


async def handle_user_message(state: GraphState) -> GraphState:
    # Append user message already done by caller
    # Plan tasks if queue empty or new message arrives
    if not state.task_queue:
        tasks = await plan_tasks(state.messages[-1].content)
        state.task_queue = [
            WorkflowTask(type=t["type"], params=t.get("params", {}))
            for t in tasks
        ]

    # Process tasks sequentially
    new_messages: List[ChatMessage] = []
    while state.task_queue:
        task = state.task_queue[0]
        if task.type == "leave":
            # merge slots with task params preference to task
            params = {**state.slots, **getattr(task, "params", {})}
            result = await run_leave_agent(state.user_id, params)
            if result.get("awaiting"):
                state.awaiting_user_input = True
                q = "\n".join(result["questions"])
                new_messages.append(ChatMessage(role="agent", content=q))
                break
            else:
                state.last_tool_result = result["result"]
                new_messages.append(ChatMessage(role="agent", content=f"请假已提交，编号：{result['result'].get('request_id')}", meta=result["result"]))
                state.task_queue.pop(0)
                # merge any produced params back to slots if needed
        elif task.type == "meeting":
            params = {**state.slots, **getattr(task, "params", {})}
            result = await run_meeting_agent(params)
            if result.get("awaiting"):
                state.awaiting_user_input = True
                q = "\n".join(result["questions"])
                new_messages.append(ChatMessage(role="agent", content=q))
                break
            else:
                if result.get("error"):
                    new_messages.append(ChatMessage(role="agent", content=result["error"]))
                    state.task_queue.pop(0)
                else:
                    booking = result["result"]["booking"]
                    topic = booking.get("topic")
                    rid = booking.get("room_id")
                    new_messages.append(ChatMessage(role="agent", content=f"会议室已预约：{rid}，主题：{topic}", meta=result["result"]))
                    state.last_tool_result = result["result"]
                    state.task_queue.pop(0)
        else:
            new_messages.append(ChatMessage(role="agent", content=f"暂不支持的任务类型：{task.type}"))
            state.task_queue.pop(0)

    state.messages.extend(new_messages)
    return state


async def handle_user_reply_to_questions(state: GraphState, user_message: str) -> GraphState:
    # naive parse: try to infer times and attendees from user input
    text = user_message.strip()
    # extremely simple parsing hooks; replace with robust NLP if needed
    if any(k in text for k in [":", "-", "/", "年", "月", "日"]):
        # assign to start if missing else end
        if not state.slots.get("start"):
            state.slots["start"] = text
        elif not state.slots.get("end"):
            state.slots["end"] = text
    # attendees
    for token in text.replace("人", " ").split():
        if token.isdigit():
            state.slots["attendees"] = int(token)
            break
    # topic
    if "主题" in text or "关于" in text:
        state.slots["topic"] = text

    state.awaiting_user_input = False
    return await handle_user_message(state)