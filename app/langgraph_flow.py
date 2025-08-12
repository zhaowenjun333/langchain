from __future__ import annotations
from typing import Any, Dict
from langgraph.graph import StateGraph, END
from .models import GraphState
from .graph import handle_user_message, handle_user_reply_to_questions


async def _run_turn(state: GraphState, user_message: str) -> GraphState:
    if state.awaiting_user_input:
        return await handle_user_reply_to_questions(state, user_message)
    else:
        return await handle_user_message(state)


def build_langgraph():
    graph = StateGraph(GraphState)

    async def run_node(state: GraphState) -> GraphState:
        # The last message is assumed to be the user input
        return await _run_turn(state, state.messages[-1].content if state.messages else "")

    graph.add_node("run", run_node)
    graph.set_entry_point("run")
    graph.add_edge("run", END)
    return graph.compile()