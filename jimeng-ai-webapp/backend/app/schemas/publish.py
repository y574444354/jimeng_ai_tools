"""发布管理相关请求与响应模型"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class PublishToXHSRequest(BaseModel):
    """发布到小红书请求"""
    article_id: str = Field(..., description="文章ID")
    platform_account_id: str = Field(..., description="平台账号ID")
    title: Optional[str] = Field(None, max_length=200, description="发布标题（可不同于文章标题）")
    images: List[str] = Field(default=[], description="配图路径列表")
    tags: List[str] = Field(default=[], description="发布标签")
    schedule_at: Optional[str] = Field(None, description="定时发布时间(ISO格式)")


class PublishRecordResponse(BaseModel):
    """发布记录响应"""
    id: str
    article_id: str
    article_title: Optional[str] = None
    platform: str
    platform_post_id: Optional[str] = None
    status: str
    publish_url: Optional[str] = None
    error_message: Optional[str] = None
    published_at: Optional[str] = None
    created_at: Optional[str] = None


class PlatformAccountCreate(BaseModel):
    """添加平台账号请求"""
    platform: str = Field(..., description="平台标识: xiaohongshu")
    account_name: str = Field(..., min_length=1, max_length=50, description="账号昵称")
    access_token: str = Field(..., description="授权Token")
    token_expires_at: Optional[str] = Field(None, description="Token过期时间")


class PlatformAccountUpdate(BaseModel):
    """更新平台账号请求"""
    account_name: Optional[str] = Field(None, min_length=1, max_length=50)
    access_token: Optional[str] = None
    token_expires_at: Optional[str] = None
    is_active: Optional[bool] = None


class PlatformAccountResponse(BaseModel):
    """平台账号响应"""
    id: str
    platform: str
    account_name: str
    is_active: bool = True
    token_expires_at: Optional[str] = None
    created_at: Optional[str] = None
