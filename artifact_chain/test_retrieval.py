"""召回测试脚本 - 专门测试 Wiki 知识召回效果"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.intent_parser import IntentParser
from src.wiki_kb import WikiKnowledgeBase
from src.retriever import Retriever


def test_retrieval(user_input: str):
    """测试召回效果"""
    print("\n" + "="*70)
    print(f"【测试输入】: {user_input}")
    print("="*70)

    # 1. 意图解析
    intent_parser = IntentParser()
    intent = intent_parser.parse(user_input)

    print("\n【意图解析结果】")
    print(f"  artifact (素材): {intent.artifact}")
    print(f"  style (风格): {intent.style}")
    print(f"  intent_type (意图类型): {intent.intent_type}")
    print(f"  duration (时长): {intent.duration}秒")

    # 2. 初始化 Wiki 知识库
    wiki_kb = WikiKnowledgeBase()

    print(f"\n【Wiki 知识库状态】")
    print(f"  总页面数: {len(wiki_kb.entries)}")
    print(f"  目录分布:")
    for cat in ["entities", "concepts", "summaries", "comparisons", "synthesis"]:
        count = len([e for e in wiki_kb.entries if e.category == cat])
        print(f"    - {cat}: {count}")

    # 3. 召回
    retriever = Retriever(wiki_kb)
    results = retriever.retrieve(intent)

    print(f"\n【召回结果】共 {len(results)} 条")

    for i, r in enumerate(results, 1):
        entry = r.entry
        print(f"\n--- 召回 #{i} ---")
        print(f"  标题: {entry.title}")
        print(f"  分类: {entry.category}")
        print(f"  置信度: {entry.confidence}")
        print(f"  召回分数: {r.score}")
        print(f"  匹配说明: {r.highlight}")
        print(f"  标签: {entry.tags}")
        print(f"  描述: {entry.description}")
        print(f"  相关页面: {entry.aliases}")

        # 显示内容摘要（前200字）
        content_preview = entry.content[:200].replace("\n", " ").strip()
        if len(entry.content) > 200:
            content_preview += "..."
        print(f"  内容预览: {content_preview}")

    print("\n" + "="*70)


def main():
    if len(sys.argv) > 1:
        # 命令行参数作为测试输入
        user_input = " ".join(sys.argv[1:])
        test_retrieval(user_input)
    else:
        print("\n" + "="*70)
        print("  Wiki 知识召回测试")
        print("="*70)
        print("用法: python test_retrieval.py <测试句子>")
        print("示例: python test_retrieval.py 敦煌的科幻节目策划")
        print("="*70)


if __name__ == "__main__":
    main()
