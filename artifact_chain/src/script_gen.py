"""脚本生成模块 - 简化实现"""
from dataclasses import dataclass
from typing import List


@dataclass
class ScriptResult:
    """脚本生成结果"""
    script: str
    citations: List[str]


class ScriptGenerator:
    """脚本生成器（简化实现）"""

    def generate(self, intent, retrieved_results) -> ScriptResult:
        """
        基于检索结果生成脚本（Mock实现）

        实际项目中这里会调用LLM API
        """
        # 提取素材名称
        artifact = intent.artifact or "文物"
        style = intent.style or "悬疑"
        duration = intent.duration or 60

        # 简化Mock脚本
        script = f"""【{style}风格短视频脚本】({duration}秒)

场景一：神秘开场
画面：黑暗中，青铜面具的眼睛微微发光
画外音：在三千年前的古蜀大地，隐藏着怎样的秘密...

场景二：悬念铺垫
画面：考古学家手持电筒，走进三星堆遗址
画外音：这副面具，见证了一个失落的文明

场景三：高潮揭示
画面：面具特写，眼睛的纹路仿佛在诉说历史
画外音：古蜀人用这双"纵目"，看见了怎样的天地？

场景四：留白结尾
画面：面具缓缓隐入黑暗
画外音：答案，就埋藏在这片土地之下...
"""

        # 提取引用
        citations = [r.entry.sources[0] if r.entry.sources else "" for r in retrieved_results]

        return ScriptResult(script=script, citations=citations)
