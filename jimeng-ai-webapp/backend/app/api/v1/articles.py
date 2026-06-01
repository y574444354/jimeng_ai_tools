"""
文章管理API路由
"""
import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1 import success_response, page_response
from app.models import get_db
from app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleAutoSave, ArticleGenerate,
)
from app.services.article_service import article_service
from app.services.ai_writer_service import ai_writer_service
from app.services.search_service import search_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/articles", tags=["文章管理"])


@router.post("")
async def create_article(request: ArticleCreate, db: Session = Depends(get_db)):
    """创建文章"""
    result = article_service.create(request.model_dump(), db)
    return success_response(data=result, message="文章创建成功")


@router.get("/{article_id}")
async def get_article(article_id: str, db: Session = Depends(get_db)):
    """获取文章详情"""
    result = article_service.get(article_id, db)
    return success_response(data=result)


@router.get("")
async def list_articles(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str = Query(default=None, description="筛选状态: draft/published"),
    category_id: str = Query(default=None, description="筛选分类"),
    keyword: str = Query(default=None, description="搜索关键词"),
    db: Session = Depends(get_db),
):
    """查询文章列表（分页、筛选、搜索）"""
    result = article_service.get_list(
        page=page, page_size=page_size,
        status=status, category_id=category_id, keyword=keyword,
        db=db,
    )
    return page_response(
        items=result["list"], total=result["total"],
        page=result["page"], page_size=result["pageSize"],
    )


@router.put("/{article_id}")
async def update_article(article_id: str, request: ArticleUpdate, db: Session = Depends(get_db)):
    """更新文章（自动创建版本快照）"""
    result = article_service.update(article_id, request.model_dump(exclude_none=True), db)
    return success_response(data=result, message="文章更新成功")


@router.delete("/{article_id}")
async def delete_article(article_id: str, db: Session = Depends(get_db)):
    """删除文章及关联数据"""
    article_service.delete(article_id, db)
    return success_response(message="文章删除成功")


@router.post("/{article_id}/auto-save")
async def auto_save_article(article_id: str, request: ArticleAutoSave, db: Session = Depends(get_db)):
    """自动保存草稿（不创建版本记录）"""
    result = article_service.auto_save(article_id, request.model_dump(exclude_none=True), db)
    return success_response(data=result, message="自动保存成功")


@router.get("/{article_id}/versions")
async def get_article_versions(article_id: str, db: Session = Depends(get_db)):
    """获取文章版本历史"""
    versions = article_service.get_versions(article_id, db)
    return success_response(data=versions)


@router.post("/{article_id}/versions/{version_id}/restore")
async def restore_article_version(article_id: str, version_id: str, db: Session = Depends(get_db)):
    """恢复到指定版本"""
    result = article_service.restore_version(article_id, version_id, db)
    return success_response(data=result, message="版本恢复成功")


@router.post("/{article_id}/sources")
async def save_article_sources(
    article_id: str,
    sources: list[dict],
    db: Session = Depends(get_db),
):
    """保存搜索素材到文章"""
    result = search_service.save_sources(article_id, sources, db)
    return success_response(data=result, message=f"已保存{len(result)}条素材")


@router.get("/{article_id}/sources")
async def get_article_sources(article_id: str, db: Session = Depends(get_db)):
    """获取文章的搜索素材列表"""
    result = search_service.get_sources(article_id, db)
    return success_response(data=result)


@router.post("/{article_id}/generate")
async def generate_article_content(
    article_id: str,
    request: ArticleGenerate,
    db: Session = Depends(get_db),
):
    """AI生成文章内容（基于搜索素材）"""
    # 获取素材
    sources = search_service.get_sources(article_id, db)
    if not sources:
        return success_response(data=None, message="暂无素材，请先添加搜索素材")
    # AI生成
    generated = ai_writer_service.generate_article(
        query=request.query,
        sources=sources,
        style=request.style,
    )
    return success_response(data=generated, message="AI生成完成")
