import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index
from app.models import Base


class Article(Base):
    """文章表"""
    __tablename__ = "articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="draft", index=True)  # draft/published/published_xhs
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    cover_image_path = Column(String(500), nullable=True)
    word_count = Column(Integer, nullable=False, default=0)
    view_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_article_status", "status"),
        Index("idx_article_created_at", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "status": self.status,
            "category_id": self.category_id,
            "cover_image_path": self.cover_image_path,
            "word_count": self.word_count,
            "view_count": self.view_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
