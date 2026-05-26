from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """统一API响应模型"""
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


class PageResponse(BaseModel):
    """统一分页响应模型"""
    list: List[Any]
    total: int
    page: int
    page_size: int