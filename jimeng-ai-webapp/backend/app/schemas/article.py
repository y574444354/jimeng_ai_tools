"""文章相关请求与响应模型"""
from typing import Optional, List
from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    """创建文章请求"""
    title: str = Field(..., min_length=1, max_length=200, description="文章标题")
    content: Optional[str] = Field(None, description="Markdown格式正文")
    summary: Optional[str] = Field(None, max_length=500, description="摘要")
    category_id: Optional[str] = Field(None, description="分类ID")
    tag_ids: Optional[List[str]] = Field(None, description="标签ID列表")
    cover_image_path: Optional[str] = Field(None, description="封面图路径")
    status: str = Field(default="draft", description="文章状态: draft/published")


class ArticleUpdate(BaseModel):
    """更新文章请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文章标题")
    content: Optional[str] = Field(None, description="Markdown格式正文")
    summary: Optional[str] = Field(None, max_length=500, description="摘要")
    category_id: Optional[str] = Field(None, description="分类ID")
    tag_ids: Optional[List[str]] = Field(None, description="标签ID列表")
    cover_image_path: Optional[str] = Field(None, description="封面图路径")
    status: Optional[str] = Field(None, description="文章状态")


class ArticleAutoSave(BaseModel):
    """自动保存请求"""
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = None
    summary: Optional[str] = None


class ArticleGenerate(BaseModel):
    """AI生成文章请求"""
    query: str = Field(..., min_length=1, max_length=500, description="文章主题/关键词")
    source_ids: Optional[List[str]] = Field(None, description="选中的素材ID列表")
    style: Optional[str] = Field(None, description="写作风格")
    generate_images: bool = Field(default=False, description="是否同时生成配图")


class ArticleResponse(BaseModel):
    """文章响应"""
    id: str
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    status: str
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    cover_image_path: Optional[str] = None
    word_count: int = 0
    view_count: int = 0
    tags: List[dict] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ArticleListItem(BaseModel):
    """文章列表项"""
    id: str
    title: str
    summary: Optional[str] = None
    status: str
    category_name: Optional[str] = None
    cover_image_path: Optional[str] = None
    word_count: int = 0
    tags: List[dict] = []
    created_at: Optional[str] = None


class ArticleVersionResponse(BaseModel):
    """文章版本响应"""
    id: str
    article_id: str
    version_number: int
    title: str
    content: Optional[str] = None
    change_summary: Optional[str] = None
    created_at: Optional[str] = None


class CategoryCreate(BaseModel):
    """创建分类请求"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    description: Optional[str] = Field(None, max_length=200, description="分类描述")
    sort_order: int = Field(default=0, description="排序")


class CategoryUpdate(BaseModel):
    """更新分类请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    sort_order: Optional[int] = None


class CategoryResponse(BaseModel):
    """分类响应"""
    id: str
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    article_count: int = 0
    created_at: Optional[str] = None


class TagCreate(BaseModel):
    """创建标签请求"""
    name: str = Field(..., min_length=1, max_length=30, description="标签名")
    color: str = Field(default="#6366F1", max_length=7, description="标签颜色")


class TagUpdate(BaseModel):
    """更新标签请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=30)
    color: Optional[str] = Field(None, max_length=7)


class TagResponse(BaseModel):
    """标签响应"""
    id: str
    name: str
    color: str = "#6366F1"
    article_count: int = 0
    created_at: Optional[str] = None
