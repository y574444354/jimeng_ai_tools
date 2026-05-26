import time
import logging
import json
import base64
from typing import Optional, List
from volcengine.visual.VisualService import VisualService
from app.core.config import settings
from app.core.exceptions import APIException

logger = logging.getLogger(__name__)


class JimengClient:
    """即梦AI API客户端（基于火山引擎SDK）"""

    def __init__(self):
        self._client: Optional[VisualService] = None
        self._initialized = False

    def initialize(self):
        """初始化即梦AI客户端"""
        try:
            self._client = VisualService()
            self._client.set_ak(settings.VOLC_ACCESS_KEY)
            self._client.set_sk(settings.VOLC_SECRET_KEY)
            self._initialized = True
            logger.info("即梦AI客户端初始化成功")
        except Exception as e:
            logger.error(f"即梦AI客户端初始化失败: {str(e)}")
            raise

    @property
    def client(self) -> VisualService:
        if not self._initialized or self._client is None:
            raise RuntimeError("即梦AI客户端未初始化，请先调用 initialize()")
        return self._client

    def _call_cv_process(self, form: dict) -> dict:
        """调用 cv_process 同步接口，返回标准化的图片数据"""
        try:
            resp = self.client.cv_process(form)
            code = resp.get("code")
            if code == 10000:
                # 提取 binary_data_base64 列表
                data = resp.get("data", {})
                images = []
                if isinstance(data, dict) and "binary_data_base64" in data:
                    b64_list = data["binary_data_base64"]
                    if isinstance(b64_list, list):
                        images = b64_list
                return {"status": "completed", "images": images}
            else:
                error_msg = resp.get("message", f"API返回错误码: {code}")
                logger.error(f"cv_process 调用失败: {error_msg}")
                raise APIException(f"即梦AI调用失败: {error_msg}")
        except APIException:
            raise
        except Exception as e:
            logger.error(f"cv_process 调用异常: {str(e)}")
            raise APIException(f"即梦AI调用异常: {str(e)}")

    def text2img(self, prompt: str, image_size: str, image_count: int = 1,
                 negative_prompt: Optional[str] = None, style: Optional[str] = None,
                 cfg_scale: float = 7.0, seed: int = 0) -> dict:
        """文生图 - 同步生成，直接返回图片base64列表"""
        width = int(image_size.split("x")[0])
        height = int(image_size.split("x")[1])

        # 按 image_count 调用多次，收集所有图片
        all_images = []
        for i in range(image_count):
            form = {
                "req_key": "jimeng_t2i_v40",
                "prompt": prompt,
                "width": width,
                "height": height,
                "seed": seed if seed != 0 else -1,
                "steps": 30,
                "strength": 0.8,
                "scale": cfg_scale,
            }
            if negative_prompt:
                form["negative_prompt"] = negative_prompt

            logger.info(f"文生图 [{i+1}/{image_count}]: prompt='{prompt[:50]}...', size={image_size}")
            result = self._call_cv_process(form)
            all_images.extend(result.get("images", []))

            # 多张图片时添加延迟
            if image_count > 1 and i < image_count - 1:
                time.sleep(2)

        return {"status": "completed", "images": all_images}

    def img2img(self, prompt: str, image_size: str, reference_image_path: str,
                image_count: int = 1, negative_prompt: Optional[str] = None,
                style: Optional[str] = None, cfg_scale: float = 7.0, seed: int = 0) -> dict:
        """图生图 - 同步生成，直接返回图片base64列表"""
        width = int(image_size.split("x")[0])
        height = int(image_size.split("x")[1])

        all_images = []
        for i in range(image_count):
            form = {
                "req_key": "jimeng_i2i_v30",
                "prompt": prompt,
                "binary_data_base64": [self._encode_image(reference_image_path)],
                "width": width,
                "height": height,
                "seed": seed if seed != 0 else -1,
                "scale": cfg_scale,
            }
            if negative_prompt:
                form["negative_prompt"] = negative_prompt

            logger.info(f"图生图 [{i+1}/{image_count}]: prompt='{prompt[:50]}...', size={image_size}")
            result = self._call_cv_process(form)
            all_images.extend(result.get("images", []))

            if image_count > 1 and i < image_count - 1:
                time.sleep(2)

        return {"status": "completed", "images": all_images}

    def inpainting(self, prompt: str, image_size: str, reference_image_path: str,
                   mask_image_path: str, image_count: int = 1,
                   negative_prompt: Optional[str] = None, cfg_scale: float = 7.0,
                   seed: int = 0) -> dict:
        """局部重绘 - 同步生成，直接返回图片base64列表"""
        width = int(image_size.split("x")[0])
        height = int(image_size.split("x")[1])

        all_images = []
        for i in range(image_count):
            form = {
                "req_key": "jimeng_i2i_v30",
                "prompt": prompt,
                "binary_data_base64": [
                    self._encode_image(reference_image_path),
                    self._encode_image(mask_image_path),
                ],
                "width": width,
                "height": height,
                "seed": seed if seed != 0 else -1,
                "scale": cfg_scale,
            }
            if negative_prompt:
                form["negative_prompt"] = negative_prompt

            logger.info(f"局部重绘 [{i+1}/{image_count}]: prompt='{prompt[:50]}...', size={image_size}")
            result = self._call_cv_process(form)
            all_images.extend(result.get("images", []))

            if image_count > 1 and i < image_count - 1:
                time.sleep(2)

        return {"status": "completed", "images": all_images}

    def _encode_image(self, file_path: str) -> str:
        """将图片文件编码为Base64"""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")


# 全局单例
jimeng_client = JimengClient()