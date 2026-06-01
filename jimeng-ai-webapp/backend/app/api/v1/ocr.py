"""OCR（图片识文）API路由"""
import logging
from fastapi import APIRouter

from app.api.v1 import success_response
from app.schemas.ocr import OCRRequest
from app.services.ocr_service import ocr_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ocr/recognize")
async def ocr_recognize(request: OCRRequest):
    """图片识文（OCR）"""
    logger.info(f"OCR识别请求: image_path={request.image_path}")
    result = ocr_service.recognize(request.image_path)
    return success_response(data=result, message="文字识别完成")
