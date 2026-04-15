import pytest
from artifact_chain.src.wiki_kb import WikiKnowledgeBase, WikiEntry, RetrievedEntry


def test_wiki_kb_load():
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    assert isinstance(kb.entries, list)
    assert len(kb.entries) > 0


def test_entries_have_required_fields():
    """测试 Wiki 条目包含必需字段"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    for entry in kb.entries:
        assert hasattr(entry, 'title')
        assert hasattr(entry, 'category')
        assert hasattr(entry, 'content')
        assert hasattr(entry, 'confidence')
        assert hasattr(entry, 'status')
        assert hasattr(entry, 'aliases')


def test_get_page():
    """测试获取指定页面"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    entry = kb.get_page("青铜面具")
    assert entry is not None
    assert entry.title == "青铜面具"
    assert entry.confidence == 0.75
    assert entry.status == "active"


def test_get_page_not_found():
    """测试获取不存在的页面"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    entry = kb.get_page("不存在的页面")
    assert entry is None


def test_get_page_by_alias():
    """测试通过别名获取页面"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    entry = kb.get_page("Bronze Mask")
    assert entry is not None
    assert entry.title == "青铜面具"


def test_list_pages():
    """测试列出所有页面（带过滤）"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    pages = kb.list_pages(category="entities")
    assert all(p.category == "entities" for p in pages)


def test_list_pages_by_status():
    """测试按状态列出页面"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    pages = kb.list_pages(status="active")
    assert all(p.status == "active" for p in pages)


def test_get_high_confidence_pages():
    """测试获取高置信度页面"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    pages = kb.get_high_confidence_pages(threshold=0.7)
    assert all(p.confidence >= 0.7 for p in pages)


def test_search_by_keyword():
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    results = kb.search("青铜面具")
    assert all(isinstance(r, RetrievedEntry) for r in results)
    assert all("青铜面具" in r.entry.title or "青铜面具" in r.entry.content
              for r in results)


def test_search_returns_highlight():
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    results = kb.search("三星堆")
    for r in results:
        assert r.highlight
        assert isinstance(r.highlight, str)


def test_search_no_match():
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    results = kb.search("完全不存在的关键词")
    assert len(results) == 0


def test_read_index():
    """测试读取 index.md"""
    kb = WikiKnowledgeBase("artifact_chain/wiki")
    index = kb.read_index()
    assert "Wiki Index" in index
    assert "Confidence" in index
    assert "Status" in index
