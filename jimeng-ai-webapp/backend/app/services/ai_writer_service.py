"""AI 写作辅助服务

从数据库获取激活的 AI 模型配置，调用 AIClient 生成结构化大纲和完整文章。
"""
import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.services.ai_client import ai_client
from app.services.ai_model_config_service import ai_model_config_service

logger = logging.getLogger(__name__)


class AIWriterService:
    """AI 写作辅助服务"""

    def __init__(self):
        self.max_outline_level = 3
        self.default_style = "专业分析"

    def _get_client_config(self, db: Session) -> Optional[dict]:
        """获取可用的 AI 客户端配置（优先数据库激活配置，Fallback .env）"""
        config = ai_model_config_service.get_active(db)
        if config:
            return {
                "api_base_url": config.api_base_url,
                "api_key": config.api_key,
                "model": config.model_name,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }
        # Fallback: .env 配置
        from app.core.config import settings

        if settings.AI_DEFAULT_API_BASE_URL and settings.AI_DEFAULT_API_KEY:
            return {
                "api_base_url": settings.AI_DEFAULT_API_BASE_URL,
                "api_key": settings.AI_DEFAULT_API_KEY,
                "model": settings.AI_DEFAULT_MODEL_NAME or "gpt-3.5-turbo",
                "temperature": settings.AI_DEFAULT_TEMPERATURE,
                "max_tokens": settings.AI_DEFAULT_MAX_TOKENS,
            }
        return None

    async def generate_outline(
        self, db: Session, query: str, sources: List[dict], style: str = None
    ) -> dict:
        """根据搜索素材生成文章大纲"""
        cfg = self._get_client_config(db)
        if not cfg:
            logger.warning("无可用 AI 配置，返回空结果")
            return {"title_suggestions": [], "outline": [], "summary": ""}

        style = style or self.default_style
        sources_text = self._format_sources(sources)

        system_prompt = (
            f"你是一位{style}领域的资深编辑。"
            "请根据提供的搜索素材，生成一份结构清晰的文章大纲。"
            "必须返回严格的 JSON 格式，不要包含 markdown 代码块标记。"
        )

        user_prompt = (
            f"主题：{query}\n\n"
            f"参考素材：\n{sources_text}\n\n"
            f"请生成 JSON，格式如下：\n"
            f'{{"title_suggestions": ["标题1", "标题2", "标题3"], '
            f'"outline": [{{"heading": "章节标题", "key_points": ["要点1", "要点2"]}}], '
            f'"summary": "一段文章概述"}}'
        )

        try:
            result = await ai_client.chat_completion(
                api_base_url=cfg["api_base_url"],
                api_key=cfg["api_key"],
                model=cfg["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=cfg["temperature"],
                max_tokens=cfg["max_tokens"],
                response_format={"type": "json_object"},
            )
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            parsed = json.loads(content)
            return {
                "title_suggestions": parsed.get("title_suggestions", []),
                "outline": parsed.get("outline", []),
                "summary": parsed.get("summary", ""),
            }
        except json.JSONDecodeError:
            logger.warning("AI 返回非 JSON 格式，尝试提取文本")
            return {"title_suggestions": [], "outline": [], "summary": content[:500]}
        except Exception as e:
            logger.error(f"AI 生成大纲失败: {str(e)}", exc_info=True)
            return {"title_suggestions": [], "outline": [], "summary": f"AI 调用失败: {str(e)}"}

    async def generate_article(
        self,
        db: Session,
        query: str,
        sources: List[dict],
        outline: List[dict] = None,
        style: str = None,
    ) -> dict:
        """根据大纲和素材生成完整文章"""
        cfg = self._get_client_config(db)
        if not cfg:
            logger.warning("无可用 AI 配置，返回空结果")
            return {"title": "", "content": "", "summary": ""}

        style = style or self.default_style
        sources_text = self._format_sources(sources)
        outline_text = self._format_outline(outline) if outline else "请根据素材自动规划文章结构。"

        system_prompt = (
            f"你是一位{style}领域的资深作者。"
            "请根据提供的大纲和素材，撰写一篇高质量的文章。"
            "文章应逻辑清晰、论证充分、可读性强。"
            "必须返回严格的 JSON 格式，不要包含 markdown 代码块标记。"
        )

        user_prompt = (
            f"主题：{query}\n\n"
            f"大纲：\n{outline_text}\n\n"
            f"参考素材：\n{sources_text}\n\n"
            f"请生成 JSON，格式如下：\n"
            f'{{"title": "文章标题", "content": "文章正文（Markdown 格式）", "summary": "文章摘要"}}'
        )

        try:
            result = await ai_client.chat_completion(
                api_base_url=cfg["api_base_url"],
                api_key=cfg["api_key"],
                model=cfg["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=cfg["temperature"],
                max_tokens=cfg["max_tokens"],
                response_format={"type": "json_object"},
            )
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            parsed = json.loads(content)
            return {
                "title": parsed.get("title", ""),
                "content": parsed.get("content", ""),
                "summary": parsed.get("summary", ""),
            }
        except json.JSONDecodeError:
            return {"title": query, "content": content, "summary": ""}
        except Exception as e:
            logger.error(f"AI 生成文章失败: {str(e)}", exc_info=True)
            return {"title": "", "content": "", "summary": f"AI 调用失败: {str(e)}"}

    def _format_sources(self, sources: List[dict]) -> str:
        """格式化搜索素材为文本"""
        if not sources:
            return "（无参考素材）"
        lines = []
        for i, s in enumerate(sources, 1):
            title = s.get("title", "无标题")
            snippet = s.get("snippet", "")
            content = s.get("content", "")
            text = content or snippet
            lines.append(f"[{i}] {title}\n{text[:500]}")
        return "\n\n".join(lines)

    def _format_outline(self, outline: List[dict]) -> str:
        """格式化大纲为文本"""
        lines = []
        for item in outline:
            heading = item.get("heading", "")
            key_points = item.get("key_points", [])
            lines.append(f"## {heading}")
            for kp in key_points:
                lines.append(f"- {kp}")
        return "\n".join(lines)


ai_writer_service = AIWriterService()
