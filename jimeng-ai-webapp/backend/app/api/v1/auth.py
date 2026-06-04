from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.api.v1 import success_response
from app.api.deps import require_auth
from app.models import get_db
from app.schemas.auth import LoginRequest, UserInfo, TokenResponse
from app.services.auth_service import auth_service
from app.core.exceptions import AuthException

router = APIRouter()


@router.post("/auth/login", summary="用户登录")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户名 + 密码登录，成功后返回 JWT 令牌"""
    user = auth_service.authenticate(db, request.username, request.password)
    if not user:
        raise AuthException(message="用户名或密码错误")

    token = auth_service.create_access_token(user["id"], user["username"])
    return success_response(
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserInfo(id=user["id"], username=user["username"]),
        ).model_dump(),
        message="登录成功",
    )


@router.get("/auth/me", summary="获取当前用户信息", dependencies=[Depends(require_auth)])
def get_current_user(
    db: Session = Depends(get_db),
    authorization: str = Header(default="", description="Bearer Token"),
):
    """获取当前登录用户的信息"""
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthException(message="未提供有效的认证令牌")

    token = authorization[len("Bearer "):]
    user = auth_service.get_current_user(db, token)
    return success_response(
        data=UserInfo(id=user["id"], username=user["username"]).model_dump(),
    )
