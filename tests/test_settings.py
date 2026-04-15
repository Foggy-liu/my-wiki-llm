import pytest
from artifact_chain.config.settings import config, Config


def test_config_defaults():
    assert config.wiki_dir.name == "wiki"
    assert config.top_k == 5
    assert config.default_style == "悬疑"
    assert config.default_duration == 60


def test_config_dataclass():
    c = Config(top_k=10)
    assert c.top_k == 10
    assert c.default_style == "悬疑"  # 默认值保持
