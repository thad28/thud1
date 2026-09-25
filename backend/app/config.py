import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    app_name: str = "AI Resume Skill Extractor & Job Skill Gap Analyzer"
    api_prefix: str = "/api"
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    demo_mode: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    max_upload_size_mb: int = 10
    allowed_extensions: list[str] = [".pdf"]

settings = Settings()
