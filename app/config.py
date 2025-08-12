from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    mongodb_uri: str = Field("mongodb://localhost:27017", alias="MONGODB_URI")
    db_name: str = Field("multiagent", alias="DB_NAME")
    llm_provider: str = Field("openai", alias="LLM_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    ollama_model: str | None = Field(default="llama3", alias="OLLAMA_MODEL")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()