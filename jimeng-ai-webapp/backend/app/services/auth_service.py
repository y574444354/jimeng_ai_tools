from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.exceptions import AuthException
from app.models.user import User


class AuthService:
    """认证服务"""

    def hash_password(self, password: str) -> str:
        """对密码进行哈希处理"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码是否匹配"""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def authenticate(self, db: Session, username: str, password: str) -> dict | None:
        """验证用户名和密码，成功返回用户字典"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user.to_dict()

    def create_access_token(self, user_id: str, username: str) -> str:
        """生成 JWT 访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "username": username,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_token(self, token: str) -> dict:
        """解析 JWT 令牌，返回 payload"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError:
            raise AuthException(message="登录凭证无效或已过期，请重新登录")

    def get_current_user(self, db: Session, token: str) -> dict:
        """从令牌获取当前用户信息"""
        payload = self.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthException(message="登录凭证无效，请重新登录")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AuthException(message="用户不存在")
        return user.to_dict()

    def ensure_default_admin(self, db: Session):
        """确保默认管理员账号存在（首次启动时创建）"""
        import secrets
        import logging
        from app.core.config import settings

        logger = logging.getLogger(__name__)
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # 优先使用环境变量密码，未设置则生成随机密码
            password = settings.ADMIN_DEFAULT_PASSWORD
            if not password:
                password = secrets.token_urlsafe(16)
                logger.warning(
                    "=" * 60 + "\n"
                    "  警告：未设置 ADMIN_DEFAULT_PASSWORD 环境变量\n"
                    f"  已生成随机管理员密码: {password}\n"
                    "  请使用该密码登录后立即修改，或在 .env 中设置固定密码\n"
                    + "=" * 60
                )
            admin = User(
                username="admin",
                password_hash=self.hash_password(password),
            )
            db.add(admin)
            db.commit()
            logger.info("默认管理员账号已创建（admin）")


auth_service = AuthService()
