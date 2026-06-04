"""
智能搜索API路由
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1 import success_response
from app.models import get_db
from app.schemas.search import WebSearchRequest, SummarizeRequest
from app.services.search_service import search_service
from app.services.ai_writer_service import ai_writer_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["智能搜索"])


@router.post("/web")
async def search_web(request: WebSearchRequest):
    """全网搜索"""
    result = search_service.search_web(
        query=request.query,
        max_results=request.max_results,
        language=request.language,
    )
    return success_response(data=result, message=f"搜索完成，找到{result['total_found']}条结果")


@router.post("/summarize")
async def summarize_search_results(request: SummarizeRequest, db: Session = Depends(get_db)):
    """AI总结搜索结果，生成文章大纲和正文"""
    # 生成大纲
    outline_result = await ai_writer_service.generate_outline(
        db=db,
        query=request.query,
        sources=[s.model_dump() for s in request.sources],
        style=request.style,
    )
    # 如果素材足够，生成完整正文
    if request.sources:
        article_result = await ai_writer_service.generate_article(
            db=db,
            query=request.query,
            sources=[s.model_dump() for s in request.sources],
            outline=outline_result.get("outline", []),
            style=request.style,
        )
        outline_result["full_content"] = article_result.get("content", "")
    return success_response(data=outline_result, message="AI总结完成")
