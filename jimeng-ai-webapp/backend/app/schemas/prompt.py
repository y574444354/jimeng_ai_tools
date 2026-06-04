"""Prompt 优化相关 Schema"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class PromptOptimizeRequest(BaseModel):
    """Prompt 优化请求"""
    prompt: str = Field(..., description="用户输入的原始提示词", min_length=1, max_length=1000)
    action: Optional[Literal["optimize", "expand", "translate"]] = Field(default="optimize", description="操作类型: optimize(优化) / expand(扩写) / translate(翻译为英文)")
    style: Optional[str] = Field(default=None, description="期望的图片风格，用于引导优化方向")


class PromptOptimizeResponse(BaseModel):
    """Prompt 优化响应"""
    original_prompt: str = Field(..., description="原始提示词")
    optimized_prompt: str = Field(..., description="优化后的提示词")
    action: str = Field(..., description="执行的操作类型")
