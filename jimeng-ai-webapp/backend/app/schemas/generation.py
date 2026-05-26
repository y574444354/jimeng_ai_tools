from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class GenerationCreate(BaseModel):
    """创建生成请求基础模型"""
    prompt: str = Field(..., max_length=1000, description="正向提示词")
    negative_prompt: Optional[str] = Field(None, max_length=500, description="负面提示词")
    image_size: str = Field(default="1024x1024", description="图片尺寸，格式:宽x高")
    style: Optional[str] = Field(None, description="图片风格")
    cfg_scale: float = Field(default=7.0, ge=1.0, le=20.0, description="提示词相关性")
    seed: int = Field(default=0, description="随机种子，0表示随机")
    image_count: int = Field(default=1, ge=1, le=4, description="生成数量")

    @field_validator("image_size")
    @classmethod
    def validate_image_size(cls, v):
        parts = v.split("x")
        if len(parts) != 2:
            raise ValueError("图片尺寸格式不正确，应为 宽x高，如 1024x1024")
        try:
            w, h = int(parts[0]), int(parts[1])
            if w <= 0 or h <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("图片尺寸必须为正整数")
        return v


class Text2ImgRequest(GenerationCreate):
    """文生图请求"""
    pass


class Img2ImgRequest(GenerationCreate):
    """图生图请求"""
    reference_image_path: str = Field(..., description="参考图片本地路径")


class InpaintingRequest(GenerationCreate):
    """局部重绘请求"""
    reference_image_path: str = Field(..., description="原图本地路径")
    mask_image_path: str = Field(..., description="遮罩图本地路径")


class GenerationStatus(BaseModel):
    """任务状态模型"""
    generation_id: str
    status: str  # pending / processing / completed / failed
    error_message: Optional[str] = None


class ImageInfo(BaseModel):
    """图片信息"""
    id: str
    image_index: int
    file_path: str
    file_size: Optional[int] = None


class GenerationResponse(BaseModel):
    """生成记录响应模型"""
    id: str
    task_type: str
    prompt: str
    negative_prompt: Optional[str] = None
    image_size: str
    style: Optional[str] = None
    cfg_scale: float
    seed: int
    image_count: int
    status: str
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
    images: List[ImageInfo] = []


class GenerationListItem(BaseModel):
    """历史记录列表项"""
    id: str
    task_type: str
    prompt: str
    image_size: str
    style: Optional[str] = None
    status: str
    image_count: int
    created_at: str
    thumbnail_path: Optional[str] = None  # 第一张图片的缩略图路径