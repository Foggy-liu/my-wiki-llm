"""文物IP内容自动化生产链 - 主入口"""
from src.intent_parser import IntentParser
from src.wiki_kb import WikiKnowledgeBase
from src.retriever import Retriever
from src.script_gen import ScriptGenerator
from src.prompt_gen import PromptGenerator


def main():
    # 初始化各模块
    intent_parser = IntentParser()
    wiki_kb = WikiKnowledgeBase()
    retriever = Retriever(wiki_kb)
    script_gen = ScriptGenerator()
    prompt_gen = PromptGenerator()

    # 用户输入
    user_input = "以青铜面具为主角，写一个60秒悬疑风短视频脚本。"

    # 1. 意图解析
    intent = intent_parser.parse(user_input)
    print(f"【意图解析】{intent}")

    # 2. Wiki检索
    results = retriever.retrieve(intent)
    print(f"【资料层】检索到 {len(results)} 条知识")

    # 3. 脚本生成
    script_result = script_gen.generate(intent, results)
    print(f"【生成层】生成脚本:\n{script_result.script}")

    # 4. Prompt转化
    prompt_result = prompt_gen.generate(script_result, intent)
    print(f"【对接层】生成Prompt:\n{prompt_result.prompt}")

    return prompt_result


if __name__ == "__main__":
    main()
