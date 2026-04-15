"""交互式入口 - 手动输入并查看输出"""
from src.intent_parser import IntentParser
from src.wiki_kb import WikiKnowledgeBase
from src.retriever import Retriever
from src.script_gen import ScriptGenerator
from src.prompt_gen import PromptGenerator

import sys
import io

# 设置 stdout 编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def run_pipeline(user_input: str) -> dict:
    """运行完整链路"""
    # 初始化各模块
    intent_parser = IntentParser()
    wiki_kb = WikiKnowledgeBase()
    retriever = Retriever(wiki_kb)
    script_gen = ScriptGenerator()
    prompt_gen = PromptGenerator()

    # 1. 意图解析
    intent = intent_parser.parse(user_input)

    # 2. Wiki检索
    results = retriever.retrieve(intent)

    # 3. 脚本生成
    script_result = script_gen.generate(intent, results)

    # 4. Prompt转化
    prompt_result = prompt_gen.generate(script_result, intent)

    return {
        "intent": intent,
        "knowledge_count": len(results),
        "script": script_result.script,
        "citations": script_result.citations,
        "prompt": prompt_result.prompt,
        "platform": prompt_result.platform
    }


def print_result(result: dict):
    """格式化输出结果"""
    intent = result["intent"]

    print("\n" + "="*60)
    print("【意图解析】")
    print(f"  素材/文物: {intent.artifact}")
    print(f"  意图类型: {intent.intent_type}")
    print(f"  风格: {intent.style}")
    print(f"  时长: {intent.duration}秒")

    print(f"\n【资料层】检索到 {result['knowledge_count']} 条知识")

    print(f"\n【生成层】生成的脚本:")
    print("-"*60)
    print(result["script"])

    print(f"\n【引用来源】")
    for cite in result["citations"]:
        print(f"  - {cite}")

    print(f"\n【对接层】生成的Prompt (平台: {result['platform']}):")
    print("-"*60)
    print(result["prompt"])
    print("="*60 + "\n")


def main():
    print("\n" + "="*60)
    print("  文物IP内容自动化生产链 - 交互式界面")
    print("="*60)
    print("输入您的创意需求，例如：")
    print("  以青铜面具为主角，写一个60秒悬疑风短视频脚本")
    print("  关于三星堆的科普视频脚本")
    print("  输入 'quit' 或 'q' 退出")
    print("="*60 + "\n")

    while True:
        try:
            user_input = input("【请输入】> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'q', '退出']:
                print("再见！")
                break

            result = run_pipeline(user_input)
            print_result(result)

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}\n")


if __name__ == "__main__":
    main()
