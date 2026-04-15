"""意图解析模块 - 从用户输入中提取意图、素材、风格等信息"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class UserIntent:
    """用户意图"""
    raw_input: str               # 原始输入
    artifact: Optional[str] = None  # 文物/素材（青铜面具）
    intent_type: Optional[str] = None  # 意图类型（脚本/视频/文案）
    style: Optional[str] = None   # 风格（悬疑/科普/喜剧）
    duration: Optional[int] = None  # 时长（秒）


class IntentParser:
    """意图解析器"""

    # 意图类型关键词
    INTENT_KEYWORDS = {
        "脚本": ["脚本", "剧本", "文案"],
        "视频": ["视频", "影片"],
        "文案": ["文案", "推广"]
    }

    # 风格关键词
    STYLE_KEYWORDS = {
        "悬疑": ["悬疑", "神秘", "惊悚"],
        "科普": ["科普", "教育", "知识"],
        "喜剧": ["喜剧", "搞笑", "幽默"],
        "剧情": ["剧情", "感人", "情感"],
        "古风": ["古风", "古典", "传统"],
        "科幻": ["科幻", "未来", "科技"],
        "浪漫": ["浪漫", "爱情", "唯美", "温情"]
    }

    # 素材/文物关键词
    ARTIFACT_KEYWORDS = {
        "青铜面具": ["青铜面具", "面具"],
        "三星堆": ["三星堆", "古蜀"],
        "敦煌莫高窟": ["敦煌", "壁画", "莫高窟", "千佛洞"],
        "唐三彩": ["唐三彩", "三彩", "陶俑"],
        "龙门石窟": ["龙门石窟", "龙门", "伊阙"],
        "故宫博物院": ["故宫", "紫禁城", "明清"]
    }

    def parse(self, user_input: str) -> UserIntent:
        """
        解析用户输入，提取意图信息
        """
        intent = UserIntent(raw_input=user_input)

        # 提取意图类型
        intent.intent_type = self._extract_intent_type(user_input)

        # 提取风格
        intent.style = self._extract_style(user_input)

        # 提取时长
        intent.duration = self._extract_duration(user_input)

        # 提取素材/文物
        intent.artifact = self._extract_artifact(user_input)

        return intent

    def _extract_intent_type(self, text: str) -> Optional[str]:
        """提取意图类型"""
        for intent_type, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return intent_type
        return "脚本"  # 默认

    def _extract_style(self, text: str) -> Optional[str]:
        """提取风格"""
        for style, keywords in self.STYLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return style
        return "悬疑"  # 默认

    def _extract_duration(self, text: str) -> Optional[int]:
        """提取时长"""
        import re
        match = re.search(r'(\d+)\s*秒', text)
        if match:
            return int(match.group(1))
        return 60  # 默认60秒

    def _extract_artifact(self, text: str) -> Optional[str]:
        """提取文物/素材"""
        for artifact, keywords in self.ARTIFACT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return artifact
        return None
