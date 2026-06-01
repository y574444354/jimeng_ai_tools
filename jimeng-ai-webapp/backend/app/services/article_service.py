"""
文章业务逻辑服务
提供文章的CRUD、版本管理、自动保存等功能
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.article import Article
from app.models.article_version import ArticleVersion
from app.models.article_source import ArticleSource
from app.models.category import Category
from app.models.tag import Tag, article_tags
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class ArticleService:
    """文章管理服务"""

    def create(self, data: dict, db: Session) -> dict:
        """创建文章"""
        tag_ids = data.pop("tag_ids", None)
        article = Article(**data)
        # 计算字数
        if article.content:
            article.word_count = len(article.content)
        db.add(article)
        db.flush()
        # 关联标签
        if tag_ids:
            self._set_tags(article.id, tag_ids, db)
        db.commit()
        db.refresh(article)
        logger.info(f"文章已创建: id={article.id}, title='{article.title}'")
        return self._build_detail(article, db)

    def get(self, article_id: str, db: Session) -> dict:
        """获取文章详情"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise NotFoundException("文章不存在")
        # 增加阅读次数
        article.view_count += 1
        db.commit()
        return self._build_detail(article, db)

    def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        category_id: Optional[str] = None,
        keyword: Optional[str] = None,
        db: Session = None,
    ) -> dict:
        """分页查询文章列表"""
        query = db.query(Article)
        if status:
            query = query.filter(Article.status == status)
        if category_id:
            query = query.filter(Article.category_id == category_id)
        if keyword:
            query = query.filter(
                Article.title.contains(keyword) | Article.content.contains(keyword)
            )
        total = query.count()
        articles = (
            query.order_by(desc(Article.updated_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        items = []
        for a in articles:
            items.append(self._build_list_item(a, db))
        return {"list": items, "total": total, "page": page, "pageSize": page_size}

    def update(self, article_id: str, data: dict, db: Session) -> dict:
        """更新文章"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise NotFoundException("文章不存在")
        tag_ids = data.pop("tag_ids", None)
        # 保存当前版本
        if data.get("content") is not None and data["content"] != article.content:
            self._create_version(article, db)
        for key, value in data.items():
            if value is not None and hasattr(article, key):
                setattr(article, key, value)
        if article.content:
            article.word_count = len(article.content)
        # 更新标签关联
        if tag_ids is not None:
            self._set_tags(article.id, tag_ids, db)
        db.commit()
        db.refresh(article)
        logger.info(f"文章已更新: id={article_id}")
        return self._build_detail(article, db)

    def delete(self, article_id: str, db: Session) -> bool:
        """删除文章及关联数据"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise NotFoundException("文章不存在")
        # 删除关联素材
        db.query(ArticleSource).filter(ArticleSource.article_id == article_id).delete()
        # 删除版本记录
        db.query(ArticleVersion).filter(ArticleVersion.article_id == article_id).delete()
        # 清除标签关联
        db.execute(article_tags.delete().where(article_tags.c.article_id == article_id))
        # 删除文章
        db.delete(article)
        db.commit()
        logger.info(f"文章已删除: id={article_id}")
        return True

    def auto_save(self, article_id: str, data: dict, db: Session) -> dict:
        """自动保存草稿（不创建版本记录）"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise NotFoundException("文章不存在")
        for key, value in data.items():
            if value is not None and hasattr(article, key):
                setattr(article, key, value)
        if article.content:
            article.word_count = len(article.content)
        db.commit()
        db.refresh(article)
        return self._build_detail(article, db)

    def get_versions(self, article_id: str, db: Session) -> list:
        """获取文章版本历史"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise NotFoundException("文章不存在")
        versions = (
            db.query(ArticleVersion)
            .filter(ArticleVersion.article_id == article_id)
            .order_by(desc(ArticleVersion.version_number))
            .all()
        )
        return [v.to_dict() for v in versions]

    def restore_version(self, article_id: str, version_id: str, db: Session) -> dict:
        """恢复到指定版本"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise NotFoundException("文章不存在")
        version = (
            db.query(ArticleVersion)
            .filter(ArticleVersion.id == version_id, ArticleVersion.article_id == article_id)
            .first()
        )
        if not version:
            raise NotFoundException("版本记录不存在")
        # 保存当前状态为新版本
        self._create_version(article, db)
        # 恢复版本内容
        article.title = version.title
        article.content = version.content
        if article.content:
            article.word_count = len(article.content)
        db.commit()
        db.refresh(article)
        logger.info(f"文章已恢复到版本v{version.version_number}: id={article_id}")
        return self._build_detail(article, db)

    def _set_tags(self, article_id: str, tag_ids: list, db: Session):
        """设置文章标签关联"""
        # 清除旧关联
        db.execute(article_tags.delete().where(article_tags.c.article_id == article_id))
        # 设置新关联
        for tag_id in tag_ids:
            db.execute(article_tags.insert().values(article_id=article_id, tag_id=tag_id))

    def _create_version(self, article: Article, db: Session):
        """创建文章版本快照"""
        latest = (
            db.query(ArticleVersion)
            .filter(ArticleVersion.article_id == article.id)
            .order_by(desc(ArticleVersion.version_number))
            .first()
        )
        version_num = (latest.version_number + 1) if latest else 1
        version = ArticleVersion(
            article_id=article.id,
            version_number=version_num,
            title=article.title,
            content=article.content,
        )
        db.add(version)

    def _build_detail(self, article: Article, db: Session) -> dict:
        """构建包含标签和分类信息的文章详情"""
        result = article.to_dict()
        # 分类信息
        if article.category_id:
            category = db.query(Category).filter(Category.id == article.category_id).first()
            result["category_name"] = category.name if category else None
        else:
            result["category_name"] = None
        # 标签信息
        tags = (
            db.query(Tag)
            .join(article_tags, Tag.id == article_tags.c.tag_id)
            .filter(article_tags.c.article_id == article.id)
            .all()
        )
        result["tags"] = [t.to_dict() for t in tags]
        return result

    def _build_list_item(self, article: Article, db: Session) -> dict:
        """构建文章列表项"""
        detail = self._build_detail(article, db)
        return {
            "id": detail["id"],
            "title": detail["title"],
            "summary": detail["summary"],
            "status": detail["status"],
            "category_name": detail["category_name"],
            "cover_image_path": detail["cover_image_path"],
            "word_count": detail["word_count"],
            "tags": detail["tags"],
            "created_at": detail["created_at"],
        }


article_service = ArticleService()
