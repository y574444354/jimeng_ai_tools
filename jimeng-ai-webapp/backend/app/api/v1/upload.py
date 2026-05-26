import os
import logging
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse
from app.api.v1 import success_response
from app.services.file_service import file_service
from app.core.config import settings
from app.core.exceptions import FileException, NotFoundException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """上传图片文件"""
    # 校验文件扩展名
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise FileException(f"不支持的图片格式: {ext}，仅支持 {', '.join(settings.ALLOWED_EXTENSIONS)}")

    # 读取文件内容
    content = await file.read()

    # 校验文件大小
    if len(content) > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise FileException(f"图片文件过大，最大允许 {max_mb:.0f}MB")

    # 保存文件
    file_path = file_service.save_upload(content, filename)

    return success_response(data={
        "file_path": file_path,
        "file_size": len(content),
        "original_name": filename,
    }, message="图片上传成功")


@router.get("/upload/file/{filename:path}")
async def get_uploaded_file(filename: str):
    """获取上传的图片文件"""
    upload_dir = os.path.abspath(os.path.join(settings.OUTPUT_DIR, "_uploads"))
    file_path = os.path.join(upload_dir, filename)
    # 安全性检查：确保不越界访问
    file_path = os.path.abspath(file_path)
    if not file_path.startswith(upload_dir):
        raise NotFoundException("文件不存在")
    if not os.path.exists(file_path):
        raise NotFoundException("文件不存在")
    return FileResponse(file_path, media_type="image/png")