import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime
from app.models import Base


class AIModelConfig(Base):
    """AI 模型配置表"""
    __tablename__ = "ai_model_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, comment="配置名称")
    api_base_url = Column(String(500), nullable=False, comment="API 基础地址")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    api_key = Column(String(500), nullable=False, comment="API 密钥")
    is_active = Column(Boolean, default=False, comment="是否激活")
    temperature = Column(Float, default=0.7, comment="温度参数")
    max_tokens = Column(Integer, default=4096, comment="最大输出 Token")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转为字典（密钥脱敏）"""
        masked_key = ""
        if self.api_key:
            masked_key = self.api_key[:4] + "****" if len(self.api_key) > 4 else "****"
        return {
            "id": self.id,
            "name": self.name,
            "api_base_url": self.api_base_url,
            "model_name": self.model_name,
            "api_key": masked_key,
            "is_active": self.is_active,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
