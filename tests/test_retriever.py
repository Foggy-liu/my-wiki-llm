import pytest
from artifact_chain.src.wiki_kb import WikiKnowledgeBase
from artifact_chain.src.retriever import Retriever
from artifact_chain.src.intent_parser import IntentParser


def test_retriever_init():
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    retriever = Retriever(kb, top_k=3)
    assert retriever.top_k == 3
    assert retriever.wiki_kb is kb


def test_retrieve_with_intent():
    """测试根据意图检索（核心测试）"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    retriever = Retriever(kb)
    parser = IntentParser()

    intent = parser.parse("以青铜面具为主角，写一个60秒悬疑风短视频脚本。")
    results = retriever.retrieve(intent)

    assert isinstance(results, list)
    assert len(results) > 0
    titles = [r.entry.title for r in results]
    assert "青铜面具" in titles


def test_retrieve_returns_high_confidence_first():
    """测试高置信度页面优先返回"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    retriever = Retriever(kb)
    parser = IntentParser()

    intent = parser.parse("关于三星堆的视频")
    results = retriever.retrieve(intent)

    if len(results) >= 2:
        assert results[0].entry.confidence >= results[1].entry.confidence


def test_retrieve_script_intent():
    """测试脚本类型意图检索"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    retriever = Retriever(kb)
    parser = IntentParser()

    intent = parser.parse("以青铜面具为主角，写一个60秒悬疑风短视频脚本。")
    results = retriever.retrieve(intent)

    titles = [r.entry.title for r in results]
    assert "短视频脚本结构" in titles


def test_get_context_for_query():
    """测试检索器提供的 LLM 上下文"""
    retriever = Retriever(WikiKnowledgeBase("artifact_chain/wiki"))
    context = retriever.get_context_for_query("如何写一个悬疑风格的青铜面具短视频脚本？")

    assert "index" in context
    assert "pages_by_category" in context
    assert "entities" in context["pages_by_category"]
    assert "concepts" in context["pages_by_category"]
    assert "high_confidence_pages" in context
