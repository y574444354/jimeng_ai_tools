"""FastAPI 公共依赖

提供认证、权限等可复用的 Depends 依赖项。
"""
import logging
from fastapi import Header, Depends
from sqlalchemy.orm import Session
from app.core.exceptions import AuthException
from app.models import get_db
from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)


def require_auth(
    authorization: str = Header(default="", description="Bearer Token"),
    db: Session = Depends(get_db),
):
    """认证依赖 — 验证 Bearer Token 并返回当前用户

    用法: @router.post("/endpoint", dependencies=[Depends(require_auth)])
    或需要用户信息时: user: dict = Depends(require_auth)
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthException(message="未提供有效的认证令牌")

    token = authorization[len("Bearer "):]
    try:
        user = auth_service.get_current_user(db, token)
        return user
    except AuthException:
        raise
    except Exception as e:
        logger.error(f"认证校验异常: {str(e)}")
        raise AuthException(message="认证校验失败，请重新登录")
