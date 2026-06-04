"""AI 模型配置请求/响应 Schema"""
from typing import Optional
from pydantic import BaseModel, Field


class AIConfigCreate(BaseModel):
    """创建 AI 配置请求"""
    name: str = Field(..., min_length=1, max_length=100, description="配置名称")
    api_base_url: str = Field(..., min_length=1, max_length=500, description="API 基础地址")
    model_name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    api_key: str = Field(..., min_length=1, max_length=500, description="API 密钥")
    temperature: float = Field(default=0.7, ge=0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=4096, ge=1, le=128000, description="最大输出 Token")


class AIConfigUpdate(BaseModel):
    """更新 AI 配置请求"""
    name: Optional[str] = Field(None, max_length=100, description="配置名称")
    api_base_url: Optional[str] = Field(None, max_length=500, description="API 基础地址")
    model_name: Optional[str] = Field(None, max_length=100, description="模型名称")
    api_key: Optional[str] = Field(None, max_length=500, description="API 密钥")
    temperature: Optional[float] = Field(None, ge=0, le=2.0, description="温度参数")
    max_tokens: Optional[int] = Field(None, ge=1, le=128000, description="最大输出 Token")


class AIConfigTest(BaseModel):
    """测试 AI 配置连通性请求"""
    api_base_url: str = Field(..., description="API 基础地址")
    model_name: str = Field(..., description="模型名称")
    api_key: str = Field(..., description="API 密钥")


class AIConfigResponse(BaseModel):
    """AI 配置响应"""
    id: str
    name: str
    api_base_url: str
    model_name: str
    api_key: str  # 已脱敏
    is_active: bool
    temperature: float
    max_tokens: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
