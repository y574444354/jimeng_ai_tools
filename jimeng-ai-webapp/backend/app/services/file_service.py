import os
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class FileService:
    """文件管理服务"""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir

    def save_image(self, image_data: bytes, task_id: str, index: int) -> str:
        """保存图片到本地

        Args:
            image_data: 图片二进制数据
            task_id: 任务ID
            index: 图片序号

        Returns:
            图片相对路径
        """
        # 按日期创建目录: ./output/YYYYMMDD/
        date_str = datetime.now().strftime("%Y%m%d")
        date_dir = os.path.join(self.output_dir, date_str)
        os.makedirs(date_dir, exist_ok=True)

        # 文件名: {task_id}_{index}.png
        filename = f"{task_id}_{index}.png"
        file_path = os.path.join(date_dir, filename)

        # 写入文件
        with open(file_path, "wb") as f:
            f.write(image_data)

        # 获取文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"图片已保存: {file_path} ({file_size} bytes)")

        # 返回相对路径
        return f"{date_str}/{filename}"

    def delete_image(self, relative_path: str) -> bool:
        """删除图片文件

        Args:
            relative_path: 图片相对路径 (如 20240101/uuid_1.png)

        Returns:
            是否成功删除
        """
        full_path = os.path.join(self.output_dir, relative_path)
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info(f"图片已删除: {full_path}")
                return True
            else:
                logger.warning(f"图片不存在: {full_path}")
                return False
        except Exception as e:
            logger.error(f"删除图片失败: {full_path}, 错误: {str(e)}")
            return False

    def get_image_path(self, relative_path: str) -> str:
        """获取图片完整路径"""
        return os.path.join(self.output_dir, relative_path)

    def save_upload(self, file_content: bytes, filename: str) -> str:
        """保存上传的图片到临时目录

        Returns:
            保存后的完整路径
        """
        upload_dir = os.path.join(self.output_dir, "_uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # 生成唯一文件名
        import uuid
        ext = os.path.splitext(filename)[1] or ".png"
        save_name = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(upload_dir, save_name)

        with open(save_path, "wb") as f:
            f.write(file_content)

        logger.info(f"上传文件已保存: {save_path}")
        return save_path


file_service = FileService()