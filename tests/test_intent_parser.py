import pytest
from artifact_chain.src.intent_parser import IntentParser, UserIntent


def test_parse_basic():
    parser = IntentParser()
    result = parser.parse("以青铜面具为主角，写一个60秒悬疑风短视频脚本。")

    assert isinstance(result, UserIntent)
    assert result.artifact == "青铜面具"
    assert result.style == "悬疑"
    assert result.duration == 60
    assert result.intent_type == "脚本"


def test_extract_style():
    parser = IntentParser()
    result = parser.parse("写一个科普风格的视频脚本")
    assert result.style == "科普"


def test_extract_artifact():
    parser = IntentParser()
    result = parser.parse("关于三星堆的视频")
    assert result.artifact == "三星堆"


def test_default_values():
    parser = IntentParser()
    result = parser.parse("写一个短视频")
    assert result.style == "悬疑"  # 默认风格
    assert result.duration == 60  # 默认时长
