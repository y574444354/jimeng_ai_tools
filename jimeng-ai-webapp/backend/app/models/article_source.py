import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from app.models import Base


class ArticleSource(Base):
    """搜索素材表"""
    __tablename__ = "article_sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), ForeignKey("articles.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(1000), nullable=True)
    snippet = Column(Text, nullable=True)
    full_content = Column(Text, nullable=True)
    source_type = Column(String(20), nullable=False, default="web_search")  # web_search/xiaohongshu/manual
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_as_article_id", "article_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "article_id": self.article_id,
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "full_content": self.full_content,
            "source_type": self.source_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
