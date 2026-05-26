# 架构信息模型

## 需求信息

| 项目 | 内容 |
|------|------|
| 需求名称 | jimeng-ai-integration |
| 需求文档 | `.cospec/spec/jimeng-ai-integration/requirement.md` |
| 需求质量评分 | 87分 |

## 架构决策记录

| 决策ID | 决策项 | 决策结果 | 决策理由 |
|--------|-------|---------|---------|
| AD-001 | 架构模式 | 推荐架构（本地单机部署） | 需求为单用户本地部署的个人级AI工具，100用户规模，无需企业级架构 |
| AD-002 | 服务拆分 | 单体架构（1个发布单元） | 业务聚焦、复杂度低，单体架构维护成本最低 |
| AD-003 | 后端技术栈 | Python + FastAPI | 需求指定Python，FastAPI异步支持好、适合API调用场景 |
| AD-004 | 前端技术栈 | Vue3 + TypeScript + Element Plus + Vite | 已有前端UI设计稿，与需求一致 |
| AD-005 | 数据库 | SQLite | 单用户本地部署、数据实体简单，无需独立数据库服务 |
| AD-006 | 鉴权方式 | API密钥（HMAC-SHA256） | 通过.env管理即梦AI火山引擎AK/SK |
| AD-007 | 第三方集成 | 即梦AI火山引擎API | 核心需求，通过volcengine-python-sdk集成 |

## 设计文档清单

| 文档 | 路径 | 说明 |
|------|------|------|
| 系统架构文档 | `.cospec/architecture/design.md` | 系统总体架构设计 |
| 技术方案文档 | `.cospec/spec/jimeng-ai-integration/tech.md` | 本次需求技术方案（含内部接口设计） |