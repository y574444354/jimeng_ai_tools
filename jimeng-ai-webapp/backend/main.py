import logging
import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings, validate_config
from app.core.logging import logger
from app.core.exceptions import AppException, app_exception_handler, general_exception_handler
from app.api.v1 import api_router
from app.api.v1.health import router as health_router
from app.api.v1.generations import router as generations_router
from app.api.v1.upload import router as upload_router
from app.models import init_db
from app.integration.jimeng_client import jimeng_client

app = FastAPI(
    title="即梦AI图片生成系统",
    description="基于火山引擎即梦AI API的图片生成Web应用",
    version="1.0.0",
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册API路由（子路由注册到主路由）
api_router.include_router(health_router, tags=["健康检查"])
api_router.include_router(generations_router, tags=["图片生成"])
api_router.include_router(upload_router, tags=["文件上传"])
app.include_router(api_router)

# 挂载静态文件服务（用于访问生成的图片）
output_dir = os.path.abspath(settings.OUTPUT_DIR)
os.makedirs(output_dir, exist_ok=True)
app.mount("/output", StaticFiles(directory=output_dir), name="output")


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("=" * 50)
    logger.info("即梦AI图片生成系统启动中...")
    logger.info("=" * 50)

    # 1. 校验AK/SK配置
    try:
        validate_config()
        logger.info("✓ API密钥配置校验通过")
    except ValueError as e:
        logger.error(f"✗ API密钥配置校验失败: {str(e)}")
        print("\n" + "!" * 60)
        print("  错误：API密钥未配置")
        print(f"  详情：{str(e)}")
        print("!" * 60 + "\n")
        sys.exit(1)

    # 2. 初始化即梦AI客户端
    try:
        jimeng_client.initialize()
        logger.info("✓ 即梦AI客户端初始化成功")
    except Exception as e:
        logger.error(f"✗ 即梦AI客户端初始化失败: {str(e)}")
        print(f"\n错误：即梦AI客户端初始化失败 - {str(e)}\n")
        sys.exit(1)

    # 3. 初始化数据库
    try:
        init_db()
        logger.info("✓ 数据库初始化成功")
    except Exception as e:
        logger.error(f"✗ 数据库初始化失败: {str(e)}")
        sys.exit(1)

    # 4. 创建必要的目录
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    logger.info("✓ 数据目录创建完成")

    logger.info("=" * 50)
    logger.info(f"服务已启动: http://{settings.APP_HOST}:{settings.APP_PORT}")
    logger.info(f"API 文档: http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
    logger.info("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
    )