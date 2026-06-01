"""OCR（图片识文）请求与响应模型"""
from typing import List
from pydantic import BaseModel


class OCRRequest(BaseModel):
    """OCR识别请求"""
    image_path: str  # 已上传的图片路径


class OCRTextLine(BaseModel):
    """单行文字识别结果"""
    text: str         # 识别的文字内容
    confidence: float # 识别置信度
    bbox: dict        # 边界框，包含 x/y/width/height
    type: str = "body"  # 类型：title 标题 / body 正文


class OCRSection(BaseModel):
    """识别段落（按间距分组后的结果）"""
    type: str = "body"            # 段落类型：title 标题 / body 正文
    lines: List[OCRTextLine]      # 段落内各行文字
    text: str                     # 合并后的段落纯文本


class OCRResponse(BaseModel):
    """OCR识别完整响应"""
    image_path: str             # 识别的图片路径
    raw_text: str               # 全部识别文本（所有行合并）
    sections: List[OCRSection]  # 结构化段落列表
    total_lines: int            # 识别到的总行数
