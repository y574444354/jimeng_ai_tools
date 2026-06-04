"""AI 模型配置 CRUD 服务"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ai_model_config import AIModelConfig

logger = logging.getLogger(__name__)


class AIModelConfigService:
    """AI 模型配置管理服务"""

    def get_all(self, db: Session) -> List[AIModelConfig]:
        """获取所有配置"""
        return db.query(AIModelConfig).order_by(AIModelConfig.created_at.desc()).all()

    def get_by_id(self, db: Session, config_id: str) -> Optional[AIModelConfig]:
        """根据 ID 获取配置"""
        return db.query(AIModelConfig).filter(AIModelConfig.id == config_id).first()

    def get_active(self, db: Session) -> Optional[AIModelConfig]:
        """获取当前激活的配置"""
        return db.query(AIModelConfig).filter(AIModelConfig.is_active.is_(True)).first()

    def create(self, db: Session, data: dict) -> AIModelConfig:
        """创建新配置"""
        config = AIModelConfig(**data)
        db.add(config)
        db.commit()
        db.refresh(config)
        logger.info(f"创建 AI 模型配置: name='{config.name}'")
        return config

    def update(self, db: Session, config_id: str, data: dict) -> Optional[AIModelConfig]:
        """更新配置"""
        config = self.get_by_id(db, config_id)
        if not config:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(config, key, value)
        db.commit()
        db.refresh(config)
        logger.info(f"更新 AI 模型配置: id={config_id}")
        return config

    def delete(self, db: Session, config_id: str) -> bool:
        """删除配置"""
        config = self.get_by_id(db, config_id)
        if not config:
            return False
        db.delete(config)
        db.commit()
        logger.info(f"删除 AI 模型配置: id={config_id}")
        return True

    def activate(self, db: Session, config_id: str) -> Optional[AIModelConfig]:
        """激活指定配置（先取消所有激活，再激活目标）"""
        config = self.get_by_id(db, config_id)
        if not config:
            return None
        # 取消所有激活
        db.query(AIModelConfig).filter(AIModelConfig.is_active.is_(True)).update(
            {"is_active": False}
        )
        # 激活目标
        config.is_active = True
        db.commit()
        db.refresh(config)
        logger.info(f"激活 AI 模型配置: name='{config.name}'")
        return config

    def to_response(self, config: AIModelConfig) -> dict:
        """转为 API 响应格式"""
        return config.to_dict()


ai_model_config_service = AIModelConfigService()
