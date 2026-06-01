"""
发布管理服务
负责多平台（小红书等）的内容发布和发布记录管理
"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.article import Article
from app.models.publish_record import PublishRecord
from app.models.platform_account import PlatformAccount
from app.integration.xiaohongshu_client import xiaohongshu_client
from app.core.exceptions import NotFoundException, APIException

logger = logging.getLogger(__name__)


class PublishService:
    """发布管理服务"""

    def publish_to_xiaohongshu(self, data: dict, db: Session) -> dict:
        """发布文章到小红书

        Args:
            data: 发布请求数据
                - article_id: 文章ID
                - platform_account_id: 平台账号ID
                - title: 发布标题
                - images: 配图路径列表
                - tags: 标签列表
            db: 数据库会话

        Returns:
            发布记录
        """
        article_id = data["article_id"]
        account_id = data["platform_account_id"]

        # 校验文章
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise NotFoundException("文章不存在")

        # 校验平台账号
        account = db.query(PlatformAccount).filter(
            PlatformAccount.id == account_id, PlatformAccount.is_active == True
        ).first()
        if not account:
            raise NotFoundException("平台账号不存在或已禁用")

        # 创建发布记录
        publish_title = data.get("title") or article.title
        record = PublishRecord(
            article_id=article_id,
            platform="xiaohongshu",
            status="pending",
        )
        db.add(record)
        db.flush()

        try:
            # 调用小红书API发布
            result = xiaohongshu_client.create_note(
                title=publish_title,
                content=article.content or "",
                images=data.get("images", []),
                tags=data.get("tags", []),
                access_token=account.access_token or "",
            )
            record.platform_post_id = result.get("note_id", "")
            record.status = "published"
            record.publish_url = result.get("url", "")
            record.published_at = datetime.utcnow()
            # 更新文章状态
            article.status = "published_xhs"
            db.commit()
            db.refresh(record)
            logger.info(f"文章已发布到小红书: article_id={article_id}, note_id={record.platform_post_id}")
        except Exception as e:
            record.status = "failed"
            record.error_message = str(e)
            db.commit()
            logger.error(f"发布到小红书失败: {str(e)}")

        return record.to_dict()

    def get_records(
        self, page: int = 1, page_size: int = 20, platform: Optional[str] = None, db: Session = None
    ) -> dict:
        """查询发布记录列表"""
        query = db.query(PublishRecord)
        if platform:
            query = query.filter(PublishRecord.platform == platform)
        total = query.count()
        records = (
            query.order_by(desc(PublishRecord.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        items = []
        for r in records:
            item = r.to_dict()
            # 添加文章标题
            article = db.query(Article).filter(Article.id == r.article_id).first()
            item["article_title"] = article.title if article else None
            items.append(item)
        return {"list": items, "total": total, "page": page, "pageSize": page_size}

    def get_record(self, record_id: str, db: Session) -> dict:
        """获取发布记录详情"""
        record = db.query(PublishRecord).filter(PublishRecord.id == record_id).first()
        if not record:
            raise NotFoundException("发布记录不存在")
        result = record.to_dict()
        article = db.query(Article).filter(Article.id == record.article_id).first()
        result["article_title"] = article.title if article else None
        return result

    def add_account(self, data: dict, db: Session) -> dict:
        """添加平台账号"""
        account = PlatformAccount(**data)
        db.add(account)
        db.commit()
        db.refresh(account)
        logger.info(f"平台账号已添加: platform={account.platform}, name={account.account_name}")
        return account.to_dict()

    def get_accounts(self, platform: Optional[str] = None, db: Session = None) -> list:
        """获取平台账号列表"""
        query = db.query(PlatformAccount)
        if platform:
            query = query.filter(PlatformAccount.platform == platform)
        accounts = query.order_by(desc(PlatformAccount.created_at)).all()
        return [a.to_dict() for a in accounts]

    def update_account(self, account_id: str, data: dict, db: Session) -> dict:
        """更新平台账号"""
        account = db.query(PlatformAccount).filter(PlatformAccount.id == account_id).first()
        if not account:
            raise NotFoundException("平台账号不存在")
        for key, value in data.items():
            if value is not None and hasattr(account, key):
                setattr(account, key, value)
        db.commit()
        db.refresh(account)
        return account.to_dict()

    def delete_account(self, account_id: str, db: Session) -> bool:
        """删除平台账号"""
        account = db.query(PlatformAccount).filter(PlatformAccount.id == account_id).first()
        if not account:
            raise NotFoundException("平台账号不存在")
        db.delete(account)
        db.commit()
        logger.info(f"平台账号已删除: id={account_id}")
        return True


publish_service = PublishService()
