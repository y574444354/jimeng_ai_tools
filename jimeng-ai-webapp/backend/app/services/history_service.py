import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.generation_record import GenerationRecord
from app.models.generated_image import GeneratedImage
from app.services.file_service import file_service
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class HistoryService:
    """历史记录管理服务"""

    def get_list(self, page: int = 1, page_size: int = 20, db: Session = None) -> dict:
        """分页查询历史记录列表"""
        query = db.query(GenerationRecord).order_by(desc(GenerationRecord.created_at))

        total = query.count()
        records = query.offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for record in records:
            # 获取第一张图片作为缩略图
            first_image = db.query(GeneratedImage).filter(
                GeneratedImage.generation_record_id == record.id
            ).order_by(GeneratedImage.image_index).first()

            thumbnail_path = None
            if first_image:
                thumbnail_path = f"/output/{first_image.file_path}"

            items.append({
                "id": record.id,
                "task_type": record.task_type,
                "prompt": record.prompt[:100] + "..." if len(record.prompt) > 100 else record.prompt,
                "image_size": record.image_size,
                "style": record.style,
                "status": record.status,
                "image_count": record.image_count,
                "created_at": record.created_at.isoformat() if record.created_at else None,
                "thumbnail_path": thumbnail_path,
            })

        return {
            "list": items,
            "total": total,
            "page": page,
            "pageSize": page_size,
        }

    def get_detail(self, generation_id: str, db: Session) -> dict:
        """获取历史记录详情"""
        record = db.query(GenerationRecord).filter(GenerationRecord.id == generation_id).first()
        if not record:
            raise NotFoundException("生成记录不存在")

        images = db.query(GeneratedImage).filter(
            GeneratedImage.generation_record_id == generation_id
        ).order_by(GeneratedImage.image_index).all()

        result = record.to_dict()
        result["images"] = []
        for img in images:
            img_dict = img.to_dict()
            img_dict["url"] = f"/output/{img.file_path}"
            result["images"].append(img_dict)

        return result

    def delete(self, generation_id: str, db: Session) -> bool:
        """删除历史记录及关联的图片文件"""
        record = db.query(GenerationRecord).filter(GenerationRecord.id == generation_id).first()
        if not record:
            raise NotFoundException("生成记录不存在")

        # 删除关联的图片文件
        images = db.query(GeneratedImage).filter(
            GeneratedImage.generation_record_id == generation_id
        ).all()

        for img in images:
            file_service.delete_image(img.file_path)
            db.delete(img)

        # 删除记录
        db.delete(record)
        db.commit()

        logger.info(f"历史记录已删除: generation_id={generation_id}")
        return True


history_service = HistoryService()