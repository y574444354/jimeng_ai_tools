"""
共享测试夹具 - 为所有API测试提供FastAPI TestClient、Mock数据库和Mock雪桥AI客户端

Mock策略：使用unittest.mock.patch在service/API层面拦截jimeng_client引用，
因为这些模块通过 from ... import 持有对单例的本地引用。
"""
import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
# 预先导入模型类，确保其表定义注册到Base.metadata
# （正常启动流程中的init_db会导入，但测试中需要显式导入）
from app.models.generation_record import GenerationRecord  # noqa: F401
from app.models.generated_image import GeneratedImage  # noqa: F401


# ==================== 测试用的假图片数据 ====================

# 最小1x1 PNG图片的base64编码
FAKE_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
    "+P+/HgAFhAJ/4pUo/wAAAABJRU5ErkJggg=="
)

# 最小1x1 PNG图片二进制
FAKE_PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f'
    b'\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
)


# ==================== 数据库Mock ====================

@pytest.fixture
def mock_db_session():
    """创建内存SQLite数据库会话，用于测试"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# ==================== 临时图片文件（用于图生图/局部重绘测试） ====================

@pytest.fixture
def temp_image_file():
    """创建临时PNG图片文件，返回文件路径"""
    fd, path = tempfile.mkstemp(suffix=".png", prefix="test_ref_")
    with os.fdopen(fd, "wb") as f:
        f.write(FAKE_PNG_BYTES)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def temp_mask_file():
    """创建临时遮罩图文件，返回文件路径"""
    fd, path = tempfile.mkstemp(suffix=".png", prefix="test_mask_")
    with os.fdopen(fd, "wb") as f:
        f.write(FAKE_PNG_BYTES)
    yield path
    if os.path.exists(path):
        os.unlink(path)


# ==================== Mock 雪桥AI客户端 ====================

@pytest.fixture
def mock_jimeng_client():
    """Mock 雪桥AI客户端，返回假图片base64数据"""
    client = MagicMock()
    client._initialized = True
    client.text2img.return_value = {
        "status": "completed",
        "images": [FAKE_PNG_BASE64],
    }
    client.img2img.return_value = {
        "status": "completed",
        "images": [FAKE_PNG_BASE64, FAKE_PNG_BASE64],
    }
    client.inpainting.return_value = {
        "status": "completed",
        "images": [FAKE_PNG_BASE64],
    }
    return client


# ==================== 应用 + 客户端 ====================

@pytest.fixture
def app_with_mocks(mock_db_session, mock_jimeng_client):
    """使用mock依赖创建FastAPI TestClient

    在service层mock jimeng_client，同时覆盖数据库依赖。
    因为generation_service通过 from...import 持有jimeng_client的本地引用，
    所以必须在service模块级别patch。
    """
    # 在导入app之前先patch各个引用了jimeng_client的位置
    with patch(
        "app.services.generation_service.jimeng_client", mock_jimeng_client
    ), patch(
        "app.api.v1.health.jimeng_client", mock_jimeng_client
    ):
        from main import app
        from app.models import get_db

        # 覆盖数据库依赖为测试DB
        def _override_get_db():
            try:
                yield mock_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = _override_get_db

        yield TestClient(app)

        app.dependency_overrides.clear()


@pytest.fixture
def app_without_mocks():
    """创建不mock业务服务的TestClient（用于健康检查等不需要外部API的测试）"""
    from app.models import get_db

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    from main import app
    app.dependency_overrides[get_db] = _override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
