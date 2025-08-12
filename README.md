# Multi-Agent Workflow Orchestrator (FastAPI + LangChain + LangGraph + MongoDB)

This service provides a single entrypoint to an interactive multi-agent system that can execute office workflows (e.g., leave requests and meeting room booking) from natural language, with state management and history persisted to MongoDB. It supports streaming updates via Server-Sent Events (SSE).

## Features
- Multi-agent orchestration using LangGraph (Coordinator + specialized agents)
- Tools for leave request and meeting booking (stubbed; replace with real APIs)
- MongoDB-backed session state and chat history
- Interactive slot-filling to request required/optional parameters
- SSE streaming endpoint for live progress updates
- Pluggable LLMs via LangChain (OpenAI or Ollama)

## Quickstart
1. Create a `.env` (see `.env.example`).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Environment
Copy `.env.example` to `.env` and set values as needed.

- `MONGODB_URI`: MongoDB connection string
- `DB_NAME`: Database name
- `LLM_PROVIDER`: `openai` or `ollama`
- `OPENAI_API_KEY`: If using OpenAI
- `OLLAMA_MODEL`: If using Ollama (e.g., `llama3`)

## Endpoints
- `POST /chat/stream` (SSE): Streaming interaction. Body:
  ```json
  { "user_id": "u123", "session_id": "s123", "message": "请假和预约会议室，明天上午，一小时，12人" }
  ```
- `POST /chat`: Non-streaming; returns final result after orchestration completes.
- `GET /sessions/{session_id}/history`: Retrieve chat history.

## Notes
- Tools are implemented with stubs in `app/tools`. Replace with your actual business APIs or MCP tools.
- This is a starting point. Extend agents and tools to fit your org's workflows.
