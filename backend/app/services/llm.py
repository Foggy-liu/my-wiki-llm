import httpx
from typing import Optional, List, Dict, Any
from app.config import settings

class LLMService:
    """MiniMax LLM Service wrapper"""

    def __init__(self):
        self.api_key = settings.MINIMAX_API_KEY
        self.base_url = settings.MINIMAX_BASE_URL
        self.model = settings.MINIMAX_MODEL

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/text/chatcompletion_v2",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def extract_entities(self, content: str) -> List[Dict[str, Any]]:
        prompt = f"""从以下文档中提取实体信息。返回 JSON 数组格式：
[
  {{
    "title": "实体名称",
    "category": "entities|concepts|summaries|comparisons|synthesis",
    "description": "简短描述",
    "properties": {{"属性名": "属性值"}},
    "sources": ["相关源文件"]
  }}
]

文档内容：
{content[:8000]}

只返回 JSON，不要其他内容。"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.chat(messages)

        import json
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        return []

    async def query_knowledge(self, question: str, context: str) -> Dict[str, Any]:
        prompt = f"""基于以下维基百科内容回答问题。如果内容不足以回答，说明不知道。

问题：{question}

上下文：
{context[:6000]}

请以以下 JSON 格式返回：
{{
  "answer": "回答内容",
  "sources": ["来源页面1", "来源页面2"],
  "confidence": 0.8
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.chat(messages)

        import json
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        return {"answer": response, "sources": [], "confidence": 0.5}

llm_service = LLMService()
