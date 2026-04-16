from pydantic_settings import BaseSettings
from pathlib import Path

# Project root is parent of backend/ directory
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Artifact Wiki"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = f"sqlite:///{PROJECT_ROOT}/artifact_wiki.db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Wiki paths
    WIKI_ROOT: Path = PROJECT_ROOT / "wiki"
    RAW_DIR: Path = WIKI_ROOT / "raw"
    WIKI_DIR: Path = WIKI_ROOT / "wiki"

    # MiniMax LLM
    MINIMAX_API_KEY: str = ""
    MINIMAX_BASE_URL: str = "https://api.minimax.chat/v1"
    MINIMAX_MODEL: str = "abab6.5s-chat"

    class Config:
        env_file = PROJECT_ROOT / ".env"
        extra = "allow"

settings = Settings()
