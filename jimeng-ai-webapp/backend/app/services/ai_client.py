"""OpenAI 兼容 HTTP 调用客户端

基于 httpx.AsyncClient 发送 chat completions 请求，兼容 OpenAI / DeepSeek / 千问 等 API 格式。
"""
import json
import logging
import time
import httpx
from typing import Optional, List, AsyncGenerator

logger = logging.getLogger(__name__)


class AIClient:
    """OpenAI 兼容异步 HTTP 调用客户端"""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def chat_completion(
        self,
        api_base_url: str,
        api_key: str,
        model: str,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[dict] = None,
    ) -> dict:
        """调用 chat completions API

        Args:
            api_base_url: API 基础地址（如 https://api.openai.com/v1）
            api_key: API 密钥
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大输出 token
            response_format: 响应格式，如 {"type": "json_object"}

        Returns:
            API 原始响应字典

        Raises:
            httpx.HTTPError: 网络或 API 错误
        """
        url = api_base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        logger.info(f"调用 AI API: url={url}, model={model}")

        response = await self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    async def test_connection(self, api_base_url: str, api_key: str, model: str) -> dict:
        """测试 API 连通性

        发送一条简短消息验证连接是否正常。

        Returns:
            {"ok": True, "model": "...", "latency_ms": 123} 或 {"ok": False, "error": "..."}
        """
        start = time.time()
        try:
            result = await self.chat_completion(
                api_base_url=api_base_url,
                api_key=api_key,
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
            )
            latency_ms = int((time.time() - start) * 1000)
            content = ""
            choices = result.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")
            return {
                "ok": True,
                "model": result.get("model", model),
                "latency_ms": latency_ms,
                "reply_preview": content[:100],
            }
        except httpx.HTTPError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            logger.error(f"测试连接异常: {str(e)}")
            return {"ok": False, "error": str(e)}

    async def close(self):
        """释放 HTTP 客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None


ai_client = AIClient()
