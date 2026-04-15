"""召回率检测模块"""
import os
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict
from dataclasses import dataclass

# 配置 LLM
os.environ['ANTHROPIC_BASE_URL'] = 'https://api.minimaxi.com/anthropic'
os.environ['ANTHROPIC_AUTH_TOKEN'] = 'sk-cp-os7y1GrOmjzZAyeWQpuEwn5IljJGL9jIIR1HLr_uoGBTM3Jo3nipauVN_bvhB9Gwf34LyeeTQZYbWoLxmKpIVo8BkjYpbNA53aLB7qUoxJipRCoSm898jsY'

from artifact_chain.src.intent_parser import IntentParser
from artifact_chain.src.wiki_kb import WikiKnowledgeBase
from artifact_chain.src.retriever import Retriever


@dataclass
class RecallTestCase:
    """召回测试用例"""
    query: str
    expected_pages: List[str]  # 期望召回的页面
    description: str = ""


@dataclass
class RecallResult:
    """召回结果"""
    query: str
    expected: List[str]
    actual: List[str]
    recall: float  # 召回率
    precision: float  # 准确率
    missing: List[str]  # 漏召的页面
    extra: List[str]  # 误召的页面


class RecallEvaluator:
    """召回率评估器"""

    def __init__(self):
        self.intent_parser = IntentParser()
        self.wiki_kb = WikiKnowledgeBase("artifact_chain/wiki")
        self.retriever = Retriever(self.wiki_kb)

        # 构建 ground truth 测试集
        self.test_cases = self._build_test_set()

    def _build_test_set(self) -> List[RecallTestCase]:
        """构建测试集"""
        return [
            # 三星堆 + 悬疑
            RecallTestCase(
                query="以青铜面具为主角，写一个60秒悬疑风短视频脚本",
                expected_pages=["青铜面具", "悬疑叙事技巧", "短视频脚本结构"],
                description="悬疑风格文物脚本"
            ),
            # 敦煌 + 古风
            RecallTestCase(
                query="敦煌壁画古风短视频",
                expected_pages=["敦煌莫高窟", "古风叙事技巧"],
                description="古风敦煌主题"
            ),
            # 唐三彩 + 科幻
            RecallTestCase(
                query="唐三彩科幻风格视频",
                expected_pages=["唐三彩", "科幻叙事技巧"],
                description="科幻唐三彩主题"
            ),
            # 故宫 + 浪漫
            RecallTestCase(
                query="故宫浪漫爱情故事",
                expected_pages=["故宫博物院", "浪漫叙事技巧"],
                description="浪漫故宫主题"
            ),
            # 龙门石窟
            RecallTestCase(
                query="龙门石窟科普视频",
                expected_pages=["龙门石窟", "科普", "短视频脚本结构"],
                description="龙门石窟科普"
            ),
            # 多文物组合
            RecallTestCase(
                query="敦煌和故宫的对比视频",
                expected_pages=["敦煌莫高窟", "故宫博物院"],
                description="多文物对比"
            ),
            # 悬疑单独
            RecallTestCase(
                query="悬疑风格短视频",
                expected_pages=["悬疑叙事技巧"],
                description="纯悬疑风格"
            ),
        ]

    def evaluate_retrieve(self, use_llm: bool = False) -> List[RecallResult]:
        """评估检索召回率"""
        results = []

        for tc in self.test_cases:
            intent = self.intent_parser.parse(tc.query)

            if use_llm:
                retrieved = self.retriever.retrieve_with_llm(intent, tc.query)
            else:
                retrieved = self.retriever.retrieve(intent)

            actual_pages = [r.entry.title for r in retrieved]

            # 计算召回
            hit_pages = [p for p in tc.expected_pages if p in actual_pages]
            missing_pages = [p for p in tc.expected_pages if p not in actual_pages]
            extra_pages = [p for p in actual_pages if p not in tc.expected_pages]

            recall = len(hit_pages) / len(tc.expected_pages) if tc.expected_pages else 0
            precision = len(hit_pages) / len(actual_pages) if actual_pages else 0

            results.append(RecallResult(
                query=tc.query,
                expected=tc.expected_pages,
                actual=actual_pages,
                recall=recall,
                precision=precision,
                missing=missing_pages,
                extra=extra_pages
            ))

        return results

    def print_report(self, results: List[RecallResult], method_name: str):
        """打印评估报告"""
        print(f"\n{'='*70}")
        print(f" 召回率评估报告 - {method_name}")
        print(f"{'='*70}")

        total_recall = sum(r.recall for r in results) / len(results)
        total_precision = sum(r.precision for r in results) / len(results)

        print(f"\n平均召回率: {total_recall:.2%}")
        print(f"平均准确率: {total_precision:.2%}")
        print(f"\n{'='*70}")

        for r in results:
            print(f"\n查询: {r.query}")
            print(f"  期望: {r.expected}")
            print(f"  实际: {r.actual}")
            print(f"  召回: {r.recall:.0%} | 准确: {r.precision:.0%}")
            if r.missing:
                print(f"  漏召: {r.missing}")
            if r.extra:
                print(f"  误召: {r.extra}")

        print(f"\n{'='*70}")
        print(f" 总召回率: {total_recall:.2%} | 总准确率: {total_precision:.2%}")
        print(f"{'='*70}\n")


def main():
    evaluator = RecallEvaluator()

    # 测试规则匹配
    print("\n正在评估规则匹配召回率...")
    rule_results = evaluator.evaluate_retrieve(use_llm=False)
    evaluator.print_report(rule_results, "规则匹配")

    # 测试 LLM 辅助查询
    print("\n正在评估 LLM 辅助查询召回率...")
    llm_results = evaluator.evaluate_retrieve(use_llm=True)
    evaluator.print_report(llm_results, "LLM 辅助查询")

    # 对比
    avg_recall_llm = sum(r.recall for r in llm_results) / len(llm_results)
    avg_precision_llm = sum(r.precision for r in llm_results) / len(llm_results)
    avg_recall_rule = sum(r.recall for r in rule_results) / len(rule_results)
    avg_precision_rule = sum(r.precision for r in rule_results) / len(rule_results)

    print("\n对比结果:")
    print(f"{'方法':<15} {'召回率':<10} {'准确率':<10}")
    print("-" * 35)
    print(f"{'规则匹配':<15} {avg_recall_rule:.2%}     {avg_precision_rule:.2%}")
    print(f"{'LLM辅助':<15} {avg_recall_llm:.2%}     {avg_precision_llm:.2%}")


if __name__ == "__main__":
    main()
