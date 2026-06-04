import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 火山引擎雪桥AI配置
    VOLC_ACCESS_KEY: str = ""
    VOLC_SECRET_KEY: str = ""

    # 应用配置
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True

    # JWT 配置
    JWT_SECRET_KEY: str = "change-me-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时

    # 管理员默认密码（首次启动时使用，登录后请修改）
    ADMIN_DEFAULT_PASSWORD: str = ""

    # 数据库
    DATABASE_URL: str = "sqlite:///./data/jimeng-ai.db"

    # 图片存储
    OUTPUT_DIR: str = "./output"

    # 雪桥AI API配置
    JIMENG_API_TIMEOUT: int = 120  # 任务超时时间（秒）
    JIMENG_POLL_INTERVAL: int = 2  # 轮询间隔（秒）
    JIMENG_MAX_POLL_TIME: int = 120  # 最大轮询时间（秒）

    # 上传限制
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png"}

    # 小红书开放平台配置
    XHS_APP_ID: str = ""
    XHS_APP_SECRET: str = ""
    XHS_API_BASE_URL: str = "https://open-api.xiaohongshu.com"
    XHS_REDIRECT_URI: str = ""

    # 网络搜索配置
    SEARCH_MAX_RESULTS: int = 10
    SEARCH_TIMEOUT: int = 30
    SEARCH_DEFAULT_LANGUAGE: str = "zh"

    # AI写作配置
    AI_WRITER_MAX_OUTLINE_LEVEL: int = 3
    AI_WRITER_DEFAULT_STYLE: str = "专业分析"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# 启动时校验AK/SK
def validate_config():
    """校验关键配置是否完整"""
    missing = []
    if not settings.VOLC_ACCESS_KEY or settings.VOLC_ACCESS_KEY == "your_access_key_here":
        missing.append("VOLC_ACCESS_KEY")
    if not settings.VOLC_SECRET_KEY or settings.VOLC_SECRET_KEY == "your_secret_key_here":
        missing.append("VOLC_SECRET_KEY")
    if missing:
        raise ValueError(
            f"环境变量 {', '.join(missing)} 未配置。\n"
            f"请在 backend/.env 文件中填写火山引擎的 AccessKey 和 SecretKey。\n"
            f"获取方式：登录火山引擎控制台 → 安全凭证 → API密钥"
        )