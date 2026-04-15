import pytest
from artifact_chain.src.intent_parser import IntentParser
from artifact_chain.src.wiki_kb import WikiKnowledgeBase
from artifact_chain.src.retriever import Retriever
from artifact_chain.src.script_gen import ScriptGenerator
from artifact_chain.src.prompt_gen import PromptGenerator


def test_full_pipeline():
    """测试完整链路"""
    intent_parser = IntentParser()
    wiki_kb = WikiKnowledgeBase("artifact_chain/wiki")
    retriever = Retriever(wiki_kb)
    script_gen = ScriptGenerator()
    prompt_gen = PromptGenerator()

    user_input = "以青铜面具为主角，写一个60秒悬疑风短视频脚本。"

    # 1. 意图解析
    intent = intent_parser.parse(user_input)
    assert intent.artifact == "青铜面具"
    assert intent.style == "悬疑"
    assert intent.duration == 60

    # 2. 检索（LLM 辅助）
    results = retriever.retrieve(intent)
    assert len(results) > 0

    titles = [r.entry.title for r in results]
    assert "青铜面具" in titles

    # 3. 生成脚本
    script_result = script_gen.generate(intent, results)
    assert script_result.script
    assert len(script_result.citations) > 0

    # 4. 生成Prompt
    prompt_result = prompt_gen.generate(script_result, intent)
    assert prompt_result.prompt
    assert "青铜面具" in prompt_result.prompt or "mask" in prompt_result.prompt.lower()


def test_wiki_entry_has_new_fields():
    """测试 Wiki 条目包含新字段（confidence, status, aliases）"""
    wiki_kb = WikiKnowledgeBase("artifact_chain/wiki")
    bronze_mask = wiki_kb.get_page("青铜面具")

    assert bronze_mask is not None
    assert hasattr(bronze_mask, 'confidence')
    assert hasattr(bronze_mask, 'status')
    assert hasattr(bronze_mask, 'aliases')
    assert bronze_mask.confidence > 0
    assert bronze_mask.status == "active"


def test_retriever_get_context():
    """测试检索器提供的 LLM 上下文"""
    retriever = Retriever(WikiKnowledgeBase("artifact_chain/wiki"))
    context = retriever.get_context_for_query("如何写一个悬疑风格的青铜面具短视频脚本？")

    assert "index" in context
    assert "pages_by_category" in context
    assert "entities" in context["pages_by_category"]
    assert "concepts" in context["pages_by_category"]
    assert "high_confidence_pages" in context
