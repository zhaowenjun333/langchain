from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from .config import settings


def get_chat_model(model_name: Optional[str] = None, temperature: float = 0.2):
    provider = settings.llm_provider.lower()
    if provider == "openai":
        model = model_name or "gpt-4o-mini"
        return ChatOpenAI(model=model, temperature=temperature)
    elif provider == "ollama":
        model = model_name or settings.ollama_model or "llama3"
        return ChatOllama(model=model, temperature=temperature)
    else:
        # Default to OpenAI interface; user must configure key or switch provider
        model = model_name or "gpt-4o-mini"
        return ChatOpenAI(model=model, temperature=temperature)