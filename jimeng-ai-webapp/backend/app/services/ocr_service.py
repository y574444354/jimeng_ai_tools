"""OCR（图片识文）业务逻辑服务"""
import logging
from typing import List, Optional
from app.integration.jimeng_client import JimengClient, jimeng_client as default_client

logger = logging.getLogger(__name__)


class OCRService:
    """OCR识别服务：调用API识别 + 结构化整理"""

    def __init__(self, jimeng_client: Optional[JimengClient] = None):
        """初始化OCR服务，可注入jimeng_client实例"""
        self._jimeng_client = jimeng_client or default_client

    def recognize(self, image_path: str) -> dict:
        """识别图片中的文字并返回结构化结果"""
        # 调用OCR API识别文字
        result = self._jimeng_client.ocr_recognize(image_path)
        text_lines = result.get("text_lines", [])
        # 结构化整理识别结果
        sections = self._structure_result(text_lines)
        # 合并所有行文字为原始文本
        raw_text = "\n".join(line.get("text", "") for line in text_lines)
        # 构建OCRResponse字典
        return {
            "image_path": image_path,
            "raw_text": raw_text,
            "sections": sections,
            "total_lines": len(text_lines),
        }

    def _structure_result(self, text_lines: list) -> list:
        """对识别结果进行结构化整理：排序、分组、识别标题/正文"""
        if not text_lines:
            return []
        # 按Y轴从上到下排序
        sorted_lines = sorted(text_lines, key=lambda l: l["bbox"].get("y", 0))
        # 计算平均行高
        heights = [l["bbox"].get("height", 0) for l in sorted_lines if l["bbox"].get("height", 0) > 0]
        avg_height = sum(heights) / len(heights) if heights else 20
        # 按行间距分组：相邻行Y间距超过平均行高1.5倍视为新段落
        paragraphs = []
        current_para = []
        for i, line in enumerate(sorted_lines):
            if current_para:
                prev_line = current_para[-1]
                prev_y = prev_line["bbox"].get("y", 0)
                prev_h = prev_line["bbox"].get("height", avg_height)
                curr_y = line["bbox"].get("y", 0)
                # 计算行间距（当前行顶部 - 上一行底部）
                gap = curr_y - (prev_y + prev_h)
                if gap > avg_height * 1.5:
                    # 间距过大，开始新段落
                    paragraphs.append(current_para)
                    current_para = []
            current_para.append(line)
        # 最后一个段落
        if current_para:
            paragraphs.append(current_para)
        # 每个段落内按X轴从左到右排序，识别标题
        sections = []
        for para_lines in paragraphs:
            # 段落内按X轴排序
            para_lines_sorted = sorted(para_lines, key=lambda l: l["bbox"].get("x", 0))
            # 识别标题：字体高度超过平均行高1.3倍
            para_heights = [l["bbox"].get("height", 0) for l in para_lines_sorted if l["bbox"].get("height", 0) > 0]
            para_avg_height = sum(para_heights) / len(para_heights) if para_heights else avg_height
            lines = []
            section_type = "body"
            for line in para_lines_sorted:
                line_height = line["bbox"].get("height", 0)
                line_type = "title" if line_height > para_avg_height * 1.3 else "body"
                lines.append({
                    "text": line.get("text", ""),
                    "confidence": line.get("confidence", 0),
                    "bbox": line.get("bbox", {}),
                    "type": line_type,
                })
                # 如果段落中有标题行，段落类型标记为title
                if line_type == "title":
                    section_type = "title"
            # 合并段落文本
            merged_text = self._merge_text(lines)
            sections.append({
                "type": section_type,
                "lines": lines,
                "text": merged_text,
            })
        return sections

    def _merge_text(self, lines: list) -> str:
        """将多行文字合并为段落文本"""
        texts = [line["text"] for line in lines if line.get("text")]
        return "".join(texts)


# 全局单例
ocr_service = OCRService()
