"""搜索相关请求与响应模型"""
from typing import Optional, List
from pydantic import BaseModel, Field


class WebSearchRequest(BaseModel):
    """网络搜索请求"""
    query: str = Field(..., min_length=1, max_length=500, description="搜索关键词")
    max_results: int = Field(default=10, ge=1, le=20, description="最大搜索结果数")
    language: str = Field(default="zh", description="搜索语言")


class SearchResultItem(BaseModel):
    """搜索结果项"""
    title: str
    url: Optional[str] = None
    snippet: Optional[str] = None
    content: Optional[str] = None


class WebSearchResponse(BaseModel):
    """网络搜索响应"""
    query: str
    results: List[SearchResultItem] = []
    total_found: int = 0


class SummarizeRequest(BaseModel):
    """AI总结请求"""
    query: str = Field(..., min_length=1, max_length=500, description="文章主题")
    sources: List[SearchResultItem] = Field(default=[], description="搜索素材列表")
    style: Optional[str] = Field(None, description="写作风格")


class OutlineItem(BaseModel):
    """大纲条目"""
    heading: str = ""
    key_points: List[str] = []


class SummarizeResponse(BaseModel):
    """AI总结响应"""
    title_suggestions: List[str] = []
    outline: List[OutlineItem] = []
    summary: Optional[str] = None
    full_content: Optional[str] = None


class SourceResponse(BaseModel):
    """素材响应"""
    id: str
    article_id: Optional[str] = None
    title: str
    url: Optional[str] = None
    snippet: Optional[str] = None
    full_content: Optional[str] = None
    source_type: str = "web_search"
    created_at: Optional[str] = None
