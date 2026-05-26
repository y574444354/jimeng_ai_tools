import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from app.models import Base


class GeneratedImage(Base):
    """生成图片表"""
    __tablename__ = "generated_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    generation_record_id = Column(String(36), ForeignKey("generation_records.id"), nullable=False, index=True)
    image_index = Column(Integer, nullable=False)  # 图片序号，从1开始递增
    file_path = Column(String(500), nullable=False)  # 本地文件相对路径
    file_size = Column(Integer, nullable=True)  # 文件大小（字节）
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 索引
    __table_args__ = (
        Index("idx_generation_record_id", "generation_record_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "generation_record_id": self.generation_record_id,
            "image_index": self.image_index,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }