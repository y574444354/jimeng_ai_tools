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
    """雪桥AI API客户端（基于火山引擎SDK）"""

    def __init__(self):
        self._client: Optional[VisualService] = None
        self._initialized = False

    def initialize(self):
        """初始化雪桥AI客户端"""
        try:
            self._client = VisualService()
            self._client.set_ak(settings.VOLC_ACCESS_KEY)
            self._client.set_sk(settings.VOLC_SECRET_KEY)
            # 注册OCR API信息
            self._client.set_api_info("OCRNormal", "2020-08-26")
            self._initialized = True
            logger.info("雪桥AI客户端初始化成功")
        except Exception as e:
            logger.error(f"雪桥AI客户端初始化失败: {str(e)}")
            raise

    @property
    def client(self) -> VisualService:
        if not self._initialized or self._client is None:
            raise RuntimeError("雪桥AI客户端未初始化，请先调用 initialize()")
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
                raise APIException(f"雪桥AI调用失败: {error_msg}")
        except APIException:
            raise
        except Exception as e:
            logger.error(f"cv_process 调用异常: {str(e)}")
            raise APIException(f"雪桥AI调用异常: {str(e)}")

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

    def ocr_recognize(self, image_path: str) -> dict:
        """图片识文（OCR）- 识别图片中的文字信息"""
        # 将图片编码为Base64
        encoded = self._encode_image(image_path)
        # 构造OCR请求参数（使用 ocr_api 接口，参数为 image_base64）
        form = {"image_base64": encoded}
        try:
            # 调用 OCR 专用接口 OCNormal
            resp = self.client.ocr_api("OCRNormal", form)
            code = resp.get("code")
            if code == 10000:
                # 成功：提取 line_texts 文字识别结果
                data = resp.get("data", {})
                line_texts = data.get("line_texts", [])
                # 转换为统一格式
                text_lines = []
                for line in line_texts:
                    text_line = {
                        "text": line.get("text", ""),
                        "confidence": float(line.get("confidence") or 0),
                    }
                    # bbox 可能直接是 dict，也可能需要从 x/y/width/height 重组
                    bbox = line.get("bbox")
                    if isinstance(bbox, dict):
                        text_line["bbox"] = bbox
                    elif isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                        text_line["bbox"] = {
                            "x": bbox[0],
                            "y": bbox[1],
                            "width": bbox[2],
                            "height": bbox[3],
                        }
                    else:
                        # 兼容：字段平铺在 line 中
                        text_line["bbox"] = {
                            "x": line.get("x", 0),
                            "y": line.get("y", 0),
                            "width": line.get("width", 0),
                            "height": line.get("height", 0),
                        }
                    text_lines.append(text_line)
                logger.info(f"OCR识别完成: 图片={image_path}, 识别到{len(text_lines)}行文字")
                return {"text_lines": text_lines}
            else:
                # 失败：记录日志并抛出异常
                error_msg = resp.get("message", f"OCR API返回错误码: {code}")
                logger.error(f"OCR识别失败: {error_msg}")
                raise APIException(f"OCR识别失败: {error_msg}")
        except APIException:
            raise
        except Exception as e:
            logger.error(f"OCR识别调用异常: {str(e)}")
            raise APIException(f"OCR识别调用异常: {str(e)}")

    def _encode_image(self, file_path: str) -> str:
        """将图片文件编码为Base64"""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")


# 全局单例
jimeng_client = JimengClient()