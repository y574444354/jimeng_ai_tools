import base64
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.generation_record import GenerationRecord
from app.models.generated_image import GeneratedImage
from app.integration.jimeng_client import jimeng_client
from app.services.file_service import file_service
from app.core.exceptions import APIException, NotFoundException

logger = logging.getLogger(__name__)


class GenerationService:
    """图片生成业务逻辑服务"""

    def _build_response(self, record: GenerationRecord, db: Session) -> dict:
        """构建包含图片列表的响应字典"""
        images = db.query(GeneratedImage).filter(
            GeneratedImage.generation_record_id == record.id
        ).order_by(GeneratedImage.image_index).all()
        result = record.to_dict()
        result["images"] = [img.to_dict() for img in images]
        return result

    def submit_text2img(self, request_data: dict, db: Session) -> dict:
        """提交文生图任务，同步等待完成后返回结果（含图片列表）"""
        record = GenerationRecord(
            task_type="text2img",
            prompt=request_data["prompt"],
            negative_prompt=request_data.get("negative_prompt"),
            image_size=request_data["image_size"],
            style=request_data.get("style"),
            cfg_scale=request_data.get("cfg_scale", 7.0),
            seed=request_data.get("seed", 0),
            image_count=request_data.get("image_count", 1),
            status="pending",
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        try:
            result = jimeng_client.text2img(
                prompt=record.prompt,
                image_size=record.image_size,
                image_count=record.image_count,
                negative_prompt=record.negative_prompt,
                style=record.style,
                cfg_scale=record.cfg_scale,
                seed=record.seed,
            )

            images_data = result.get("images", [])
            self._save_images(record, images_data, db)

            record.status = "completed"
            db.commit()
            db.refresh(record)

            logger.info(f"文生图任务完成: record_id={record.id}, 生成图片{len(images_data)}张")
            return self._build_response(record, db)

        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            db.commit()
            logger.error(f"文生图任务失败: {str(e)}")
            raise APIException(f"文生图任务失败: {str(e)}")

    def submit_img2img(self, request_data: dict, db: Session) -> dict:
        """提交图生图任务，同步等待完成后返回结果"""
        record = GenerationRecord(
            task_type="img2img",
            prompt=request_data["prompt"],
            negative_prompt=request_data.get("negative_prompt"),
            image_size=request_data["image_size"],
            style=request_data.get("style"),
            cfg_scale=request_data.get("cfg_scale", 7.0),
            seed=request_data.get("seed", 0),
            image_count=request_data.get("image_count", 1),
            reference_image_path=request_data.get("reference_image_path"),
            status="pending",
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        try:
            result = jimeng_client.img2img(
                prompt=record.prompt,
                image_size=record.image_size,
                reference_image_path=record.reference_image_path,
                image_count=record.image_count,
                negative_prompt=record.negative_prompt,
                style=record.style,
                cfg_scale=record.cfg_scale,
                seed=record.seed,
            )

            images_data = result.get("images", [])
            self._save_images(record, images_data, db)

            record.status = "completed"
            db.commit()
            db.refresh(record)

            logger.info(f"图生图任务完成: record_id={record.id}, 生成图片{len(images_data)}张")
            return self._build_response(record, db)

        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            db.commit()
            logger.error(f"图生图任务失败: {str(e)}")
            raise APIException(f"图生图任务失败: {str(e)}")

    def submit_inpainting(self, request_data: dict, db: Session) -> dict:
        """提交局部重绘任务，同步等待完成后返回结果"""
        record = GenerationRecord(
            task_type="inpainting",
            prompt=request_data["prompt"],
            negative_prompt=request_data.get("negative_prompt"),
            image_size=request_data["image_size"],
            style=request_data.get("style"),
            cfg_scale=request_data.get("cfg_scale", 7.0),
            seed=request_data.get("seed", 0),
            image_count=request_data.get("image_count", 1),
            reference_image_path=request_data.get("reference_image_path"),
            mask_image_path=request_data.get("mask_image_path"),
            status="pending",
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        try:
            result = jimeng_client.inpainting(
                prompt=record.prompt,
                image_size=record.image_size,
                reference_image_path=record.reference_image_path,
                mask_image_path=record.mask_image_path,
                image_count=record.image_count,
                negative_prompt=record.negative_prompt,
                cfg_scale=record.cfg_scale,
                seed=record.seed,
            )

            images_data = result.get("images", [])
            self._save_images(record, images_data, db)

            record.status = "completed"
            db.commit()
            db.refresh(record)

            logger.info(f"局部重绘任务完成: record_id={record.id}, 生成图片{len(images_data)}张")
            return self._build_response(record, db)

        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            db.commit()
            logger.error(f"局部重绘任务失败: {str(e)}")
            raise APIException(f"局部重绘任务失败: {str(e)}")

    def query_status(self, generation_id: str, db: Session) -> dict:
        """查询任务状态"""
        record = db.query(GenerationRecord).filter(GenerationRecord.id == generation_id).first()
        if not record:
            raise NotFoundException("生成记录不存在")

        return {
            "generation_id": record.id,
            "status": record.status,
            "error_message": record.error_message,
        }

    def get_generation(self, generation_id: str, db: Session) -> dict:
        """获取生成记录详情"""
        record = db.query(GenerationRecord).filter(GenerationRecord.id == generation_id).first()
        if not record:
            raise NotFoundException("生成记录不存在")

        images = db.query(GeneratedImage).filter(
            GeneratedImage.generation_record_id == generation_id
        ).order_by(GeneratedImage.image_index).all()

        result = record.to_dict()
        result["images"] = [img.to_dict() for img in images]
        return result

    def _save_images(self, record: GenerationRecord, images_data: list, db: Session):
        """保存生成的图片到存储并创建数据库记录"""
        if not images_data:
            logger.warning(f"任务返回空图片列表: record_id={record.id}")
            return

        for i, img_data in enumerate(images_data):
            # 解码base64图片数据
            if isinstance(img_data, str):
                image_bytes = base64.b64decode(img_data)
            else:
                image_bytes = img_data

            # 保存图片文件
            relative_path = file_service.save_image(image_bytes, record.id, i + 1)

            # 创建图片数据库记录
            image_record = GeneratedImage(
                generation_record_id=record.id,
                image_index=i + 1,
                file_path=relative_path,
                file_size=len(image_bytes),
            )
            db.add(image_record)

        logger.info(f"已保存{len(images_data)}张图片: record_id={record.id}")


generation_service = GenerationService()