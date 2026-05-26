from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 确保data目录存在
os.makedirs("./data", exist_ok=True)

# 创建数据库引擎
DATABASE_URL = "sqlite:///./data/jimeng-ai.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite多线程支持
    echo=False,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    """获取数据库会话（依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    from app.models.generation_record import GenerationRecord  # noqa: F401
    from app.models.generated_image import GeneratedImage  # noqa: F401
    Base.metadata.create_all(bind=engine)