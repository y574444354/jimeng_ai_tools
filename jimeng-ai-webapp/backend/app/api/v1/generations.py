import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1 import success_response, page_response
from app.models import get_db
from app.schemas.generation import Text2ImgRequest, Img2ImgRequest, InpaintingRequest
from app.services.generation_service import generation_service
from app.services.history_service import history_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generations/text2img")
async def create_text2img(request: Text2ImgRequest, db: Session = Depends(get_db)):
    """提交文生图任务"""
    result = generation_service.submit_text2img(request.model_dump(), db)
    return success_response(data=result, message="文生图生成完成")


@router.post("/generations/img2img")
async def create_img2img(request: Img2ImgRequest, db: Session = Depends(get_db)):
    """提交图生图任务"""
    result = generation_service.submit_img2img(request.model_dump(), db)
    return success_response(data=result, message="图生图生成完成")


@router.post("/generations/inpainting")
async def create_inpainting(request: InpaintingRequest, db: Session = Depends(get_db)):
    """提交局部重绘任务"""
    result = generation_service.submit_inpainting(request.model_dump(), db)
    return success_response(data=result, message="局部重绘生成完成")


@router.get("/generations/{generation_id}/status")
async def query_generation_status(generation_id: str, db: Session = Depends(get_db)):
    """查询任务状态"""
    status = generation_service.query_status(generation_id, db)
    return success_response(data=status)


@router.get("/generations/{generation_id}")
async def get_generation(generation_id: str, db: Session = Depends(get_db)):
    """获取生成结果"""
    result = generation_service.get_generation(generation_id, db)
    return success_response(data=result)


@router.get("/generations")
async def list_generations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """查询历史记录列表"""
    result = history_service.get_list(page=page, page_size=page_size, db=db)
    return page_response(
        items=result["list"],
        total=result["total"],
        page=result["page"],
        page_size=result["pageSize"],
    )


@router.delete("/generations/{generation_id}")
async def delete_generation(generation_id: str, db: Session = Depends(get_db)):
    """删除历史记录"""
    history_service.delete(generation_id, db)
    return success_response(message="删除成功")