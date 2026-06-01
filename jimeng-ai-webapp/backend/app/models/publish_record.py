import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from app.models import Base


class PublishRecord(Base):
    """发布记录表"""
    __tablename__ = "publish_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(30), nullable=False)  # xiaohongshu/wechat/...
    platform_post_id = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending/published/failed
    publish_url = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_pr_article_id", "article_id"),
        Index("idx_pr_platform", "platform"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "article_id": self.article_id,
            "platform": self.platform,
            "platform_post_id": self.platform_post_id,
            "status": self.status,
            "publish_url": self.publish_url,
            "error_message": self.error_message,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
