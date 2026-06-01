"""
发布管理API路由
"""
import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1 import success_response, page_response
from app.models import get_db
from app.schemas.publish import (
    PublishToXHSRequest,
    PlatformAccountCreate, PlatformAccountUpdate,
)
from app.services.publish_service import publish_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/publish", tags=["发布管理"])


# ========== 发布操作 ==========

@router.post("/xiaohongshu")
async def publish_to_xiaohongshu(request: PublishToXHSRequest, db: Session = Depends(get_db)):
    """发布文章到小红书"""
    result = publish_service.publish_to_xiaohongshu(request.model_dump(), db)
    return success_response(data=result, message="发布请求已提交")


@router.get("/records")
async def list_publish_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    platform: str = Query(default=None, description="筛选平台: xiaohongshu"),
    db: Session = Depends(get_db),
):
    """查询发布记录列表"""
    result = publish_service.get_records(page=page, page_size=page_size, platform=platform, db=db)
    return page_response(
        items=result["list"], total=result["total"],
        page=result["page"], page_size=result["pageSize"],
    )


@router.get("/records/{record_id}")
async def get_publish_record(record_id: str, db: Session = Depends(get_db)):
    """获取发布记录详情"""
    result = publish_service.get_record(record_id, db)
    return success_response(data=result)


# ========== 平台账号管理 ==========

@router.get("/accounts")
async def list_platform_accounts(
    platform: str = Query(default=None, description="筛选平台"),
    db: Session = Depends(get_db),
):
    """获取平台账号列表"""
    accounts = publish_service.get_accounts(platform=platform, db=db)
    return success_response(data=accounts)


@router.post("/accounts")
async def add_platform_account(request: PlatformAccountCreate, db: Session = Depends(get_db)):
    """添加平台账号"""
    result = publish_service.add_account(request.model_dump(), db)
    return success_response(data=result, message="账号添加成功")


@router.put("/accounts/{account_id}")
async def update_platform_account(
    account_id: str, request: PlatformAccountUpdate, db: Session = Depends(get_db)
):
    """更新平台账号"""
    result = publish_service.update_account(account_id, request.model_dump(exclude_none=True), db)
    return success_response(data=result, message="账号更新成功")


@router.delete("/accounts/{account_id}")
async def delete_platform_account(account_id: str, db: Session = Depends(get_db)):
    """删除平台账号"""
    publish_service.delete_account(account_id, db)
    return success_response(message="账号删除成功")
