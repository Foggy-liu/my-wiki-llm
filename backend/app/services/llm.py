import httpx
from typing import List, Dict, Any
from app.config import settings

class LLMService:
    """LLM Service wrapper - supports OpenAI and Anthropic compatible APIs"""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL.rstrip("/")
        self.model = settings.LLM_MODEL
        # Detect API format from base URL
        if "anthropic" in self.base_url:
            self.api_mode = "anthropic"
        else:
            self.api_mode = "openai"

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        if not self.api_key:
            raise ValueError("LLM_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        if self.api_mode == "anthropic":
            # Anthropic compatible API (/v1/messages)
            anthropic_messages = []
            for msg in messages:
                role = msg["role"]
                if role == "system":
                    anthropic_messages.insert(0, {"role": "user", "content": msg["content"]})
                    anthropic_messages.insert(1, {"role": "assistant", "content": "OK"})
                else:
                    anthropic_messages.append({"role": role, "content": msg["content"]})

            payload = {
                "model": self.model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            endpoint = f"{self.base_url}/messages"
        else:
            # OpenAI compatible API (/v1/chat/completions)
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            endpoint = f"{self.base_url}/chat/completions"

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if self.api_mode == "anthropic":
                for block in data["content"]:
                    if block.get("type") == "text":
                        return block["text"]
                return data["content"][0].get("text", "")
            else:
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
