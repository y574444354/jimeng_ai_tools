from fastapi import APIRouter
from app.api.v1 import success_response
from app.integration.jimeng_client import jimeng_client

router = APIRouter()


@router.get("/health")
async def health_check():
    """服务健康检查"""
    return success_response({
        "status": "healthy",
        "service": "jimeng-ai",
        "version": "1.0.0",
    })


@router.get("/health/ready")
async def health_ready():
    """服务就绪检查"""
    try:
        return success_response({
            "status": "ready",
            "database": "connected",
            "jimeng_client": "initialized" if jimeng_client._initialized else "not_initialized",
        })
    except Exception as e:
        return success_response({
            "status": "not_ready",
            "error": str(e),
        })