"""
文章分类管理API路由
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1 import success_response
from app.models import get_db
from app.models.category import Category
from app.models.article import Article
from app.schemas.article import CategoryCreate, CategoryUpdate, CategoryResponse
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/categories", tags=["分类管理"])


@router.get("")
async def list_categories(db: Session = Depends(get_db)):
    """获取分类列表（含文章数量）"""
    categories = db.query(Category).order_by(Category.sort_order).all()
    items = []
    for c in categories:
        count = db.query(Article).filter(Article.category_id == c.id).count()
        item = c.to_dict()
        item["article_count"] = count
        items.append(item)
    return success_response(data=items)


@router.post("")
async def create_category(request: CategoryCreate, db: Session = Depends(get_db)):
    """创建分类"""
    category = Category(**request.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    result = category.to_dict()
    result["article_count"] = 0
    return success_response(data=result, message="分类创建成功")


@router.put("/{category_id}")
async def update_category(category_id: str, request: CategoryUpdate, db: Session = Depends(get_db)):
    """更新分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundException("分类不存在")
    for key, value in request.model_dump(exclude_none=True).items():
        if hasattr(category, key):
            setattr(category, key, value)
    db.commit()
    db.refresh(category)
    count = db.query(Article).filter(Article.category_id == category.id).count()
    result = category.to_dict()
    result["article_count"] = count
    return success_response(data=result, message="分类更新成功")


@router.delete("/{category_id}")
async def delete_category(category_id: str, db: Session = Depends(get_db)):
    """删除分类（分类下文章的分类ID置空）"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundException("分类不存在")
    # 将使用该分类的文章category_id置空
    db.query(Article).filter(Article.category_id == category_id).update({"category_id": None})
    db.delete(category)
    db.commit()
    return success_response(message="分类删除成功")
