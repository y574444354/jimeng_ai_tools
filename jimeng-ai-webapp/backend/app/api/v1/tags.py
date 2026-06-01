"""
文章标签管理API路由
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1 import success_response
from app.models import get_db
from app.models.tag import Tag, article_tags
from app.schemas.article import TagCreate, TagUpdate
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tags", tags=["标签管理"])


@router.get("")
async def list_tags(db: Session = Depends(get_db)):
    """获取标签列表（含文章数量）"""
    tags = db.query(Tag).order_by(Tag.created_at.desc()).all()
    items = []
    for t in tags:
        count = db.execute(
            article_tags.select().where(article_tags.c.tag_id == t.id)
        ).rowcount if hasattr(db, "execute") else 0
        # 使用更可靠的方式统计关联数
        from sqlalchemy import func, select
        count_result = db.execute(
            select(func.count()).select_from(article_tags).where(article_tags.c.tag_id == t.id)
        ).scalar()
        item = t.to_dict()
        item["article_count"] = count_result or 0
        items.append(item)
    return success_response(data=items)


@router.post("")
async def create_tag(request: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    tag = Tag(**request.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    result = tag.to_dict()
    result["article_count"] = 0
    return success_response(data=result, message="标签创建成功")


@router.put("/{tag_id}")
async def update_tag(tag_id: str, request: TagUpdate, db: Session = Depends(get_db)):
    """更新标签"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise NotFoundException("标签不存在")
    for key, value in request.model_dump(exclude_none=True).items():
        if hasattr(tag, key):
            setattr(tag, key, value)
    db.commit()
    db.refresh(tag)
    result = tag.to_dict()
    return success_response(data=result, message="标签更新成功")


@router.delete("/{tag_id}")
async def delete_tag(tag_id: str, db: Session = Depends(get_db)):
    """删除标签（自动清除关联关系）"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise NotFoundException("标签不存在")
    db.execute(article_tags.delete().where(article_tags.c.tag_id == tag_id))
    db.delete(tag)
    db.commit()
    return success_response(message="标签删除成功")
