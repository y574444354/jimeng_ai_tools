# 即梦AI图片生成系统

基于 **火山引擎即梦AI API** 的 Web 应用，支持文生图、图生图、局部重绘等 AI 图片生成功能。

## 功能特性

- **文生图**：通过文本描述生成图片，支持风格、尺寸、CFG Scale 等参数调节
- **图生图**：上传参考图片，结合文本描述生成新图片
- **局部重绘**：在图片上用画笔标记区域，AI 根据描述重新绘制标记区域
- **历史记录**：查看、管理所有历史生成记录，支持缩略图预览和详情查看

## 技术栈

### 后端
| 技术 | 用途 |
|------|------|
| Python 3.11+ | 运行语言 |
| FastAPI | Web 框架 |
| SQLAlchemy 2.0 | ORM（对象关系映射） |
| SQLite | 数据库 |
| Pydantic | 数据校验与序列化 |
| volcengine-python-sdk | 即梦AI SDK |
| Uvicorn | ASGI 服务器 |

### 前端
| 技术 | 用途 |
|------|------|
| Vue 3 + TypeScript | 前端框架 |
| Vite | 构建工具 |
| Element Plus | UI 组件库 |
| Pinia | 状态管理 |
| Axios | HTTP 客户端 |
| Vue Router | 前端路由 |

## 项目结构

```
jimeng-ai-webapp/
├── frontend/                       # 前端工程（Vue 3 + Vite）
│   ├── src/
│   │   ├── api/                    # 后端接口请求封装
│   │   │   ├── request.ts          # Axios 实例（拦截器、错误处理）
│   │   │   ├── generation.ts       # 文生图/图生图/局部重绘 API
│   │   │   ├── history.ts          # 历史记录 API
│   │   │   └── upload.ts           # 图片上传 API
│   │   ├── components/             # 公共可复用组件
│   │   │   ├── GenerationResult.vue      # 生成结果展示
│   │   │   ├── ImageUploader.vue         # 图片上传组件
│   │   │   ├── InpaintCanvas.vue         # 局部重绘画布组件
│   │   │   ├── LoadingOverlay.vue        # 加载遮罩
│   │   │   ├── StatusIndicator.vue       # API 连接状态指示
│   │   │   ├── HistoryDetailModal.vue    # 历史详情弹框
│   │   │   └── DeleteConfirmModal.vue    # 删除确认弹框
│   │   ├── layouts/                # 页面布局
│   │   ├── router/                 # 前端路由配置
│   │   ├── stores/                 # 状态管理（Pinia）
│   │   └── views/                  # 业务页面
│   │       ├── Text2ImgView.vue    # 文生图页面
│   │       ├── Img2ImgView.vue     # 图生图页面
│   │       ├── InpaintView.vue     # 局部重绘页面
│   │       └── HistoryView.vue     # 历史记录页面
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/                        # 后端工程（Python FastAPI）
│   ├── app/
│   │   ├── api/v1/                 # API 路由层
│   │   │   ├── generations.py      # 图片生成及历史记录接口
│   │   │   ├── health.py           # 健康检查接口
│   │   │   └── upload.py           # 文件上传接口
│   │   ├── core/                   # 核心配置
│   │   │   ├── config.py           # 环境配置管理
│   │   │   ├── exceptions.py       # 统一异常处理
│   │   │   └── logging.py          # 日志基础设施
│   │   ├── models/                 # 数据模型
│   │   │   ├── generation_record.py # 生成记录表
│   │   │   └── generated_image.py  # 生成图片表
│   │   ├── schemas/                # 请求/响应模型
│   │   │   ├── common.py           # 统一响应模型
│   │   │   └── generation.py       # 生成相关模型
│   │   ├── services/               # 业务逻辑层
│   │   │   ├── generation_service.py # 图片生成业务
│   │   │   ├── file_service.py      # 文件管理服务
│   │   │   └── history_service.py   # 历史记录管理
│   │   └── integration/            # 第三方集成
│   │       └── jimeng_client.py    # 即梦AI API 客户端
│   ├── main.py                     # FastAPI 应用启动入口
│   ├── .env                        # 环境变量配置（AK/SK）
│   ├── requirements.txt
│   ├── data/                       # 数据库文件目录
│   └── output/                     # 图片输出目录
├── .gitignore
└── README.md
```

## 快速启动

### 前置条件

1. **Python 3.11** 或更高版本
2. **Node.js 18** 或更高版本
3. **火山引擎账号**（已开通即梦AI服务）

### 1. 配置 API 密钥

复制 `backend/.env` 文件，填写你的火山引擎密钥：

```bash
# backend/.env
VOLC_ACCESS_KEY=your_access_key_here
VOLC_SECRET_KEY=your_secret_key_here
```

> **获取方式**：登录 [火山引擎控制台](https://console.volcengine.com) → 安全凭证 → API 密钥

### 2. 启动后端服务

```bash
# 进入后端目录
cd jimeng-ai-webapp/backend

# 安装 Python 依赖
pip install -r requirements.txt

# 启动后端服务（默认 http://localhost:8000）
python main.py
```

> 后端启动会自动完成：AK/SK 校验 → 即梦AI客户端初始化 → 数据库初始化 → 目录创建。  
> 若 AK/SK 未配置，启动时会打印错误提示并退出。

### 3. 启动前端开发服务器

```bash
# 进入前端目录
cd jimeng-ai-webapp/frontend

# 安装 Node.js 依赖
npm install

# 启动前端开发服务器（默认 http://localhost:5173）
npm run dev
```

> 前端开发服务器已配置代理，`/api` 开头的请求会自动转发到 `http://localhost:8000`。

## 环境变量说明

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `VOLC_ACCESS_KEY` | 是 | — | 火山引擎 AccessKey |
| `VOLC_SECRET_KEY` | 是 | — | 火山引擎 SecretKey |
| `APP_HOST` | 否 | `0.0.0.0` | 后端监听地址 |
| `APP_PORT` | 否 | `8000` | 后端监听端口 |
| `APP_DEBUG` | 否 | `True` | 是否开启调试模式 |
| `DATABASE_URL` | 否 | `sqlite:///./data/jimeng-ai.db` | 数据库连接地址 |
| `OUTPUT_DIR` | 否 | `./output` | 图片输出目录 |

## API 文档

启动后端服务后，可通过以下地址查看自动生成的 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 核心接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/health` | 健康检查 |
| `GET` | `/api/v1/health/ready` | 服务就绪检查 |
| `POST` | `/api/v1/generations/text2img` | 提交文生图任务 |
| `POST` | `/api/v1/generations/img2img` | 提交图生图任务 |
| `POST` | `/api/v1/generations/inpainting` | 提交局部重绘任务 |
| `GET` | `/api/v1/generations/{id}` | 获取生成结果 |
| `GET` | `/api/v1/generations/{id}/status` | 查询任务状态 |
| `GET` | `/api/v1/generations` | 查询历史记录列表 |
| `DELETE` | `/api/v1/generations/{id}` | 删除历史记录 |
| `POST` | `/api/v1/upload/image` | 上传图片文件 |

## 使用指南

1. **启动服务**：按「快速启动」步骤启动后端和前端服务
2. **访问页面**：浏览器打开 `http://localhost:5173`
3. **文生图**：在「文生图」页面输入正向/负面提示词，选择图片尺寸、风格等参数，点击「生成图片」按钮
4. **图生图**：在「图生图」页面上传参考图片，输入提示词和参数，点击「生成图片」
5. **局部重绘**：在「局部重绘」页面上传图片，使用画笔标记要修改的区域，输入描述，点击「开始重绘」
6. **历史记录**：在「历史记录」页面可以查看所有生成记录，点击记录查看详情，也可以删除不需要的记录

## 数据库

项目使用 SQLite 数据库，数据库文件位于 `backend/data/jimeng-ai.db`。包含以下表：

- **generation_records**：生成记录表（任务类型、提示词、参数、状态等）
- **generated_images**：生成图片表（图片路径、文件大小等）

## 图片存储

生成的图片按日期组织存储：

```
backend/output/
├── 20240101/          # 按日期分目录
│   ├── {task_id}_1.png
│   ├── {task_id}_2.png
│   └── ...
└── _uploads/          # 用户上传的临时图片
```

## 许可证

本项目仅供学习和参考使用。