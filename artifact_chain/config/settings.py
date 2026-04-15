"""配置管理"""
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).parent.parent
WIKI_DIR = BASE_DIR / "wiki"

@dataclass
class Config:
    """系统配置"""
    wiki_dir: Path = WIKI_DIR
    top_k: int = 5  # 召回前5条最相关资料
    default_style: str = "悬疑"
    default_duration: int = 60  # 秒

config = Config()
