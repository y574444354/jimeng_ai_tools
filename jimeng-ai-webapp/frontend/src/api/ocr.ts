import request from './request'

// OCR 文本行
export interface OCRTextLine {
  text: string
  confidence: number
  bbox: { x: number; y: number; width: number; height: number }
  type: 'title' | 'body'
}

// OCR 结构化段落
export interface OCRSection {
  type: 'title' | 'body'
  lines: OCRTextLine[]
  text: string
}

// OCR 识别响应
export interface OCRResponse {
  image_path: string
  raw_text: string
  sections: OCRSection[]
  total_lines: number
}

// 图片识文请求参数
export interface OCRRequest {
  image_path: string
}

// 调用 OCR 识别接口
export async function recognizeText(imagePath: string) {
  return request.post('/ocr/recognize', { image_path: imagePath })
}
