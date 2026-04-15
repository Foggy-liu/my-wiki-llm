"""召回率测试脚本 - 批量测试 Wiki 知识召回效果"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.intent_parser import IntentParser
from src.wiki_kb import WikiKnowledgeBase
from src.retriever import Retriever


# 测试用例：每个元组 (查询语句, 期望召回的页面标题列表)
TEST_CASES = [
    # ========== 实体相关查询 ==========
    (
        "敦煌壁画的科幻节目",
        ["敦煌莫高窟", "科幻叙事技巧", "敦煌莫高窟vs龙门石窟", "文物IP短视频创作指南"]
    ),
    (
        "青铜面具的悬疑视频",
        ["青铜面具", "悬疑叙事技巧", "三星堆遗址"]
    ),
    (
        "故宫的浪漫短视频",
        ["故宫博物院", "浪漫叙事技巧", "古风叙事技巧"]
    ),
    (
        "长城的历史纪录片",
        ["长城", "古风叙事技巧", "科普叙事技巧"]
    ),
    (
        "唐三彩的介绍视频",
        ["唐三彩", "科普叙事技巧", "古风叙事技巧"]
    ),
    (
        "清明上河图的科普内容",
        ["清明上河图", "科普叙事技巧", "文物纪录片创作指南"]
    ),
    (
        "马王堆汉墓的探秘节目",
        ["马王堆汉墓", "悬疑叙事技巧", "古风叙事技巧"]
    ),
    (
        "青花瓷的工艺讲解",
        ["景德镇青花瓷", "科普叙事技巧", "唐三彩vs景德镇瓷"]
    ),
    (
        "金缕玉衣的神秘故事",
        ["金缕玉衣", "悬疑叙事技巧", "古风叙事技巧"]
    ),
    (
        "石窟艺术的对比分析",
        ["敦煌莫高窟", "龙门石窟", "云冈石窟", "敦煌莫高窟vs龙门石窟", "raw-articles-石窟艺术综合"]
    ),

    # ========== 风格相关查询 ==========
    (
        "悬疑风格的文物视频",
        ["悬疑叙事技巧", "短视频脚本结构"]
    ),
    (
        "科幻题材怎么拍文物",
        ["科幻叙事技巧", "短视频脚本结构", "文物IP短视频创作指南"]
    ),
    (
        "古风叙事有什么技巧",
        ["古风叙事技巧", "短视频脚本结构"]
    ),
    (
        "科普类文物节目怎么做",
        ["科普叙事技巧", "短视频脚本结构", "文物纪录片创作指南"]
    ),
    (
        "喜剧风格的博物馆视频",
        ["喜剧叙事技巧", "短视频脚本结构", "古风叙事技巧"]
    ),
    (
        "浪漫主题的文化短片",
        ["浪漫叙事技巧", "短视频脚本结构"]
    ),
    (
        "剧情向的文物故事",
        ["剧情叙事技巧", "短视频脚本结构"]
    ),

    # ========== 形式相关查询 ==========
    (
        "文物纪录片策划方案",
        ["文物纪录片创作指南", "科普叙事技巧", "悬疑叙事技巧"]
    ),
    (
        "博物馆直播带货脚本",
        ["文物直播带货策划", "喜剧叙事技巧", "古风叙事技巧"]
    ),
    (
        "沉浸式文物展览策划",
        ["文物互动展览策划", "科幻叙事技巧", "古风叙事技巧"]
    ),

    # ========== 干扰测试 ==========
    (
        "现代网红餐厅打卡",
        []  # 期望不召回任何文物相关内容
    ),
    (
        "最新款手机评测",
        []  # 期望不召回任何文物相关内容
    ),
    (
        "宠物猫狗饲养",
        []  # 期望不召回任何文物相关内容
    ),
    (
        "咖啡奶茶对比",
        []  # 期望不召回任何文物相关内容
    ),
]


def run_tests():
    """运行所有测试"""
    # 初始化
    intent_parser = IntentParser()
    wiki_kb = WikiKnowledgeBase()
    retriever = Retriever(wiki_kb)

    print("\n" + "="*70)
    print("  Wiki 知识召回率测试")
    print("="*70)
    print(f"\n【Wiki 知识库状态】")
    print(f"  总页面数: {len(wiki_kb.entries)}")
    for cat in ["entities", "concepts", "summaries", "comparisons", "synthesis"]:
        count = len([e for e in wiki_kb.entries if e.category == cat])
        print(f"    - {cat}: {count}")
    print("="*70)

    total = len(TEST_CASES)
    passed = 0
    failed = 0
    noise_detected = 0  # 干扰检测正确的数量

    results_detail = []

    for i, (query, expected_pages) in enumerate(TEST_CASES, 1):
        # 意图解析
        intent = intent_parser.parse(query)

        # 召回
        results = retriever.retrieve(intent)
        recalled_titles = [r.entry.title for r in results]

        # 计算命中
        if expected_pages:
            # 有期望页面的测试
            hits = set(recalled_titles) & set(expected_pages)
            precision = len(hits) / len(recalled_titles) if recalled_titles else 0
            recall = len(hits) / len(expected_pages) if expected_pages else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            status = "✅" if recall >= 0.5 else "❌"
            if recall >= 0.5:
                passed += 1
            else:
                failed += 1
        else:
            # 干扰测试：期望不召回任何页面
            if len(recalled_titles) == 0:
                status = "✅"
                passed += 1
                noise_detected += 1
                precision = recall = f1 = 1.0
            else:
                status = "❌"
                failed += 1
                precision = recall = f1 = 0.0

        results_detail.append({
            "query": query,
            "expected": expected_pages,
            "recalled": recalled_titles,
            "hits": list(hits) if expected_pages else [],
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "status": status
        })

    # 输出详细结果
    print(f"\n【测试结果】共 {total} 个测试用例")
    print(f"  通过: {passed} ✅")
    print(f"  失败: {failed} ❌")
    print(f"  召回率: {passed/total*100:.1f}%")

    print(f"\n{'='*70}")
    print("【详细结果】")
    print("="*70)

    for i, r in enumerate(results_detail, 1):
        print(f"\n#{i} {r['status']} 查询: {r['query']}")
        if r['expected']:
            print(f"   期望: {r['expected']}")
            print(f"   召回: {r['recalled']}")
            print(f"   命中: {r['hits']}")
            print(f"   P={r['precision']:.2f} R={r['recall']:.2f} F1={r['f1']:.2f}")
        else:
            print(f"   期望: 无（干扰测试）")
            print(f"   召回: {r['recalled'] if r['recalled'] else '无'}")

    # 统计信息
    print(f"\n{'='*70}")
    print("【统计信息】")

    # 计算平均指标
    relevant_tests = [r for r in results_detail if r['expected']]
    if relevant_tests:
        avg_precision = sum(r['precision'] for r in relevant_tests) / len(relevant_tests)
        avg_recall = sum(r['recall'] for r in relevant_tests) / len(relevant_tests)
        avg_f1 = sum(r['f1'] for r in relevant_tests) / len(relevant_tests)
        print(f"  相关查询平均精确率: {avg_precision:.2%}")
        print(f"  相关查询平均召回率: {avg_recall:.2%}")
        print(f"  相关查询平均F1: {avg_f1:.2%}")

    noise_tests = [r for r in results_detail if not r['expected']]
    if noise_tests:
        noise_precision = noise_detected / len(noise_tests) if noise_tests else 0
        print(f"  干扰检测正确率: {noise_precision:.2%} ({noise_detected}/{len(noise_tests)})")

    print("="*70)

    return passed, total


if __name__ == "__main__":
    run_tests()
