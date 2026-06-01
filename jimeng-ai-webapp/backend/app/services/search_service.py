"""
网络搜索服务
封装WebSearch能力，提供搜索、素材管理功能
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.article_source import ArticleSource
from app.integration.web_search_client import web_search_client, SearchResult
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class SearchService:
    """智能搜索服务"""

    def search_web(self, query: str, max_results: int = 10, language: str = "zh") -> dict:
        """全网搜索

        Args:
            query: 搜索关键词
            max_results: 最大结果数
            language: 搜索语言

        Returns:
            {"query": "...", "results": [...], "total_found": N}
        """
        logger.info(f"执行网络搜索: query='{query}', max_results={max_results}")
        # 搜索由AI运行时执行，这里返回结构化占位
        results = web_search_client.search(query, max_results, language)
        return {
            "query": query,
            "results": [self._result_to_dict(r) for r in results],
            "total_found": len(results),
        }

    def save_sources(self, article_id: str, sources: List[dict], db: Session) -> List[dict]:
        """保存搜索素材到文章

        Args:
            article_id: 文章ID
            sources: 素材列表 [{"title": ..., "url": ..., "snippet": ..., "content": ..., "source_type": ...}]
            db: 数据库会话

        Returns:
            已保存的素材列表
        """
        saved = []
        for s in sources:
            source = ArticleSource(
                article_id=article_id,
                title=s.get("title", ""),
                url=s.get("url", ""),
                snippet=s.get("snippet", ""),
                full_content=s.get("content", ""),
                source_type=s.get("source_type", "web_search"),
            )
            db.add(source)
            db.flush()
            saved.append(source.to_dict())
        db.commit()
        logger.info(f"已保存{len(saved)}条素材到文章{article_id}")
        return saved

    def get_sources(self, article_id: str, db: Session) -> List[dict]:
        """获取文章的搜索素材列表"""
        sources = (
            db.query(ArticleSource)
            .filter(ArticleSource.article_id == article_id)
            .order_by(ArticleSource.created_at)
            .all()
        )
        return [s.to_dict() for s in sources]

    def delete_source(self, source_id: str, db: Session) -> bool:
        """删除单个素材"""
        source = db.query(ArticleSource).filter(ArticleSource.id == source_id).first()
        if not source:
            raise NotFoundException("素材不存在")
        db.delete(source)
        db.commit()
        return True

    def _result_to_dict(self, result) -> dict:
        """搜索结果转为字典"""
        return {
            "title": result.title if hasattr(result, "title") else str(result),
            "url": result.url if hasattr(result, "url") else "",
            "snippet": result.snippet if hasattr(result, "snippet") else "",
            "content": result.content if hasattr(result, "content") else "",
        }


search_service = SearchService()
