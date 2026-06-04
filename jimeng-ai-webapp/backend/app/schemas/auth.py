from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=2, max_length=100, description="用户名")
    password: str = Field(..., min_length=1, max_length=255, description="密码")


class UserInfo(BaseModel):
    """用户信息（不包含敏感字段）"""
    id: str
    username: str


class TokenResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
