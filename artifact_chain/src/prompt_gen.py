"""Prompt生成模块 - 简化实现"""
from dataclasses import dataclass


@dataclass
class PromptResult:
    """Prompt生成结果"""
    prompt: str
    platform: str


class PromptGenerator:
    """Prompt生成器（简化实现）"""

    def generate(self, script_result, intent) -> PromptResult:
        """
        将脚本转化为AI视频生成Prompt（Mock实现）

        实际项目中这里会使用模板填充
        """
        platform = "sora"  # 默认平台

        prompt = f"""Cinematic footage, {intent.style or 'mysterious'} atmosphere,
ancient Chinese bronze mask as the central subject,
dramatic lighting with shadows, ultra-high definition,
bronze and gold color palette, mysterious and awe-inspiring mood.

镜头描述：
- 开场：黑暗中的青铜面具特写，眼睛发光
- 中段：考古现场，古蜀祭祀场景
- 高潮：面具特写，揭示历史秘密
- 结尾：面具隐入黑暗

风格：{intent.style or '悬疑'}古蜀文化
时长：{intent.duration or 60}秒
画面要求：电影感光影、超高清、神秘氛围
"""

        return PromptResult(prompt=prompt, platform=platform)
