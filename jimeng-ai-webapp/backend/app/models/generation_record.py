import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, Index
from app.models import Base


class GenerationRecord(Base):
    """生成记录表"""
    __tablename__ = "generation_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_type = Column(String(20), nullable=False, index=True)  # text2img / img2img / inpainting
    prompt = Column(Text, nullable=False)  # 正向提示词，最大1000字符
    negative_prompt = Column(Text, nullable=True)  # 负面提示词，最大500字符
    image_size = Column(String(20), nullable=False)  # 图片尺寸，格式"宽x高"
    style = Column(String(50), nullable=True)  # 图片风格名称
    cfg_scale = Column(Float, nullable=False, default=7.0)  # 提示词相关性 1.0~20.0
    seed = Column(Integer, nullable=False, default=0)  # 随机种子，0表示随机
    image_count = Column(Integer, nullable=False, default=1)  # 生成数量 1~4
    reference_image_path = Column(String(500), nullable=True)  # 参考图片路径
    mask_image_path = Column(String(500), nullable=True)  # 遮罩图路径
    api_task_id = Column(String(100), nullable=True, index=True)  # 即梦AI任务ID
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending/processing/completed/failed
    error_message = Column(Text, nullable=True)  # 失败时的错误描述
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 索引
    __table_args__ = (
        Index("idx_task_type", "task_type"),
        Index("idx_status", "status"),
        Index("idx_api_task_id", "api_task_id"),
        Index("idx_created_at", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "task_type": self.task_type,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "image_size": self.image_size,
            "style": self.style,
            "cfg_scale": self.cfg_scale,
            "seed": self.seed,
            "image_count": self.image_count,
            "reference_image_path": self.reference_image_path,
            "mask_image_path": self.mask_image_path,
            "api_task_id": self.api_task_id,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }