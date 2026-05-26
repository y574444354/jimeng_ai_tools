# 技术方案

## 发布单元列表
见 [`design.md`](.cospec/architecture/design.md) 发布单元列表章节

## 技术栈
见 [`design.md`](.cospec/architecture/design.md) 技术栈章节

## 项目目录结构

见 [`design.md`](.cospec/architecture/design.md) 项目目录结构章节

## 系统内部接口

### 接口规范

- 统一url格式：
/api/v1/{resource}

- 统一返回格式：
正常：
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```
异常：
```json
{
  "code": 10001,
  "message": "错误描述信息",
  "data": null
}
```

- 统一分页格式：
```json
请求：GET /api/v1/generations?page=1&pageSize=20

响应：
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [],
    "total": 100,
    "page": 1,
    "pageSize": 20
  }
}
```

### 接口列表

| 接口名 | 请求方式 | 接口URL | 请求格式 | 响应格式 | 备注 |
|--------|---------|--------|---------|----------|------|
| 提交文生图任务 | POST | /api/v1/generations/text2img | JSON | JSON | 入参包含prompt、negative_prompt、image_size、style、cfg_scale、seed、image_count |
| 提交图生图任务 | POST | /api/v1/generations/img2img | JSON | JSON | 入参包含reference_image_path + text2img参数 |
| 提交局部重绘任务 | POST | /api/v1/generations/inpainting | JSON | JSON | 入参包含reference_image_path、mask_image_path + text2img参数 |
| 查询任务状态 | GET | /api/v1/generations/{generation_id}/status | - | JSON | 返回任务状态（pending/processing/completed/failed），前端轮询 |
| 获取生成结果 | GET | /api/v1/generations/{generation_id} | - | JSON | 返回生成记录详情及生成图片列表 |
| 查询历史记录列表 | GET | /api/v1/generations | Query | JSON | 分页查询，按创建时间倒序 |
| 删除历史记录 | DELETE | /api/v1/generations/{generation_id} | - | JSON | 删除记录及关联的本地图片文件 |
| 上传参考/遮罩图片 | POST | /api/v1/upload/image | multipart/form-data | JSON | 上传图片文件，返回本地存储路径 |
| 服务健康检查 | GET | /api/v1/health | - | JSON | 返回服务运行状态 |

## OpenAPI对外接口
见 [`design.md`](.cospec/architecture/design.md) OpenAPI对外接口

## 依赖的外部接口
见 [`design.md`](.cospec/architecture/design.md) 依赖的外部接口章节

## 数据模型设计
见 [`design.md`](.cospec/architecture/design.md) 数据模型设计章节

## 系统集成
见 [`design.md`](.cospec/architecture/design.md) 系统集成章节

## 非功能设计
见 [`design.md`](.cospec/architecture/design.md) 非功能设计章节