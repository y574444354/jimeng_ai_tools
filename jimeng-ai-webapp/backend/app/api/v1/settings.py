"""系统设置 API 路由 — AI 模型配置管理"""
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import require_auth
from app.models import get_db
from app.schemas.ai_model_config import (
    AIConfigCreate,
    AIConfigUpdate,
    AIConfigTest,
)
from app.services.ai_model_config_service import ai_model_config_service
from app.services.ai_client import ai_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["系统设置"], dependencies=[Depends(require_auth)])


def success_response(data=None, message: str = "success"):
    """统一成功响应"""
    return JSONResponse(
        status_code=200,
        content={"code": 0, "message": message, "data": data},
    )


# ========== AI 模型配置 CRUD ==========


@router.get("/ai-configs")
def list_ai_configs(db: Session = Depends(get_db)):
    """获取所有 AI 模型配置列表"""
    configs = ai_model_config_service.get_all(db)
    data = [ai_model_config_service.to_response(c) for c in configs]
    return success_response(data=data, message=f"共 {len(data)} 条配置")


@router.get("/ai-configs/{config_id}")
def get_ai_config(config_id: str, db: Session = Depends(get_db)):
    """获取单个 AI 模型配置详情"""
    config = ai_model_config_service.get_by_id(db, config_id)
    if not config:
        return JSONResponse(status_code=404, content={"code": 404, "message": "配置不存在", "data": None})
    return success_response(data=ai_model_config_service.to_response(config))


@router.post("/ai-configs")
def create_ai_config(req: AIConfigCreate, db: Session = Depends(get_db)):
    """创建 AI 模型配置"""
    config = ai_model_config_service.create(db, req.model_dump())
    return success_response(data=ai_model_config_service.to_response(config), message="配置创建成功")


@router.put("/ai-configs/{config_id}")
def update_ai_config(config_id: str, req: AIConfigUpdate, db: Session = Depends(get_db)):
    """更新 AI 模型配置"""
    config = ai_model_config_service.update(db, config_id, req.model_dump(exclude_none=True))
    if not config:
        return JSONResponse(status_code=404, content={"code": 404, "message": "配置不存在", "data": None})
    return success_response(data=ai_model_config_service.to_response(config), message="配置更新成功")


@router.delete("/ai-configs/{config_id}")
def delete_ai_config(config_id: str, db: Session = Depends(get_db)):
    """删除 AI 模型配置"""
    ok = ai_model_config_service.delete(db, config_id)
    if not ok:
        return JSONResponse(status_code=404, content={"code": 404, "message": "配置不存在", "data": None})
    return success_response(message="配置已删除")


@router.post("/ai-configs/{config_id}/activate")
def activate_ai_config(config_id: str, db: Session = Depends(get_db)):
    """激活 AI 模型配置"""
    config = ai_model_config_service.activate(db, config_id)
    if not config:
        return JSONResponse(status_code=404, content={"code": 404, "message": "配置不存在", "data": None})
    return success_response(data=ai_model_config_service.to_response(config), message=f"已激活配置: {config.name}")


# ========== 连接测试 ==========


@router.post("/ai-configs/test")
def test_ai_connection(req: AIConfigTest):
    """测试 AI 模型 API 连通性"""
    result = ai_client.test_connection(
        api_base_url=req.api_base_url,
        api_key=req.api_key,
        model=req.model_name,
    )
    return success_response(data=result, message="连通性测试完成")
