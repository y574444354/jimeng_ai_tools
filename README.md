# 即梦AI图片生成系统

基于 **火山引擎即梦AI API** 的 Web 应用，支持文生图、图生图、局部重绘等 AI 图片生成与编辑功能。

## 功能特性

| 功能 | 说明 |
|------|------|
| **文生图** | 输入文本描述（提示词），AI 自动生成对应图片，支持风格、尺寸、CFG Scale 等参数调节 |
| **图生图** | 上传参考图片 + 文本描述，AI 生成与参考图风格或内容相关的新图片 |
| **局部重绘** | 上传图片后在画布上涂抹标记区域，AI 根据描述仅重绘标记部分，"指哪改哪" |
| **历史记录** | 自动记录每次生成任务，支持缩略图预览、详情查看和单条删除 |

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
jimeng_ai/
├── jimeng-ai-webapp/                  # Web 应用主工程
│   ├── backend/                       # 后端工程（Python FastAPI）
│   │   ├── app/
│   │   │   ├── api/v1/               # API 路由层
│   │   │   │   ├── generations.py     # 图片生成及历史记录接口
│   │   │   │   ├── health.py          # 健康检查接口
│   │   │   │   └── upload.py          # 文件上传接口
│   │   │   ├── core/                  # 核心配置
│   │   │   │   ├── config.py          # 环境配置管理
│   │   │   │   ├── exceptions.py      # 统一异常处理
│   │   │   │   └── logging.py         # 日志基础设施
│   │   │   ├── models/               # 数据模型（SQLAlchemy）
│   │   │   │   ├── generation_record.py
│   │   │   │   └── generated_image.py
│   │   │   ├── schemas/              # 请求/响应 Pydantic 模型
│   │   │   │   ├── common.py
│   │   │   │   └── generation.py
│   │   │   ├── services/             # 业务逻辑层
│   │   │   │   ├── generation_service.py
│   │   │   │   ├── file_service.py
│   │   │   │   └── history_service.py
│   │   │   └── integration/          # 第三方集成
│   │   │       └── jimeng_client.py   # 即梦AI API 客户端
│   │   ├── main.py                    # FastAPI 应用入口
│   │   ├── requirements.txt
│   │   ├── data/                      # 数据库文件目录
│   │   └── output/                    # 生成图片输出目录
│   ├── frontend/                      # 前端工程（Vue 3 + Vite）
│   │   ├── src/
│   │   │   ├── api/                  # 后端接口请求封装
│   │   │   ├── components/           # 公共组件
│   │   │   ├── layouts/              # 页面布局
│   │   │   ├── router/              # 前端路由
│   │   │   ├── stores/              # 状态管理（Pinia）
│   │   │   ├── styles/              # 全局样式
│   │   │   └── views/               # 业务页面
│   │   │       ├── Text2ImgView.vue   # 文生图
│   │   │       ├── Img2ImgView.vue    # 图生图
│   │   │       ├── InpaintView.vue    # 局部重绘
│   │   │       └── HistoryView.vue    # 历史记录
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── vite.config.ts
│   └── README.md                      # Web 应用详细文档
├── .cospec/                           # 项目设计文档
│   ├── architecture/                  # 架构设计
│   └── spec/                          # 需求规格
├── .gitignore
└── README.md                          # 本文件
```

## 快速启动

### 前置条件

- **Python 3.11** 或更高版本
- **Node.js 18** 或更高版本
- **火山引擎账号**（已开通即梦AI服务）

### 1. 克隆项目

```bash
git clone https://github.com/y574444354/jimeng_ai_tools.git
cd jimeng_ai
```

### 2. 配置 API 密钥

在 `jimeng-ai-webapp/backend/` 目录下创建 `.env` 文件：

```env
VOLC_ACCESS_KEY=your_access_key_here
VOLC_SECRET_KEY=your_secret_key_here
```

> 密钥获取：登录 [火山引擎控制台](https://console.volcengine.com) → 安全凭证 → API 密钥

### 3. 启动后端

```bash
cd jimeng-ai-webapp/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务（默认 http://localhost:8000）
python main.py
```

### 4. 启动前端

```bash
cd jimeng-ai-webapp/frontend

# 安装依赖
npm install

# 启动开发服务器（默认 http://localhost:5173）
npm run dev
```

浏览器打开 `http://localhost:5173` 即可使用。

## 环境变量

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `VOLC_ACCESS_KEY` | 是 | — | 火山引擎 AccessKey |
| `VOLC_SECRET_KEY` | 是 | — | 火山引擎 SecretKey |
| `APP_HOST` | 否 | `0.0.0.0` | 后端监听地址 |
| `APP_PORT` | 否 | `8000` | 后端监听端口 |
| `APP_DEBUG` | 否 | `True` | 调试模式开关 |
| `DATABASE_URL` | 否 | `sqlite:///./data/jimeng-ai.db` | 数据库连接地址 |
| `OUTPUT_DIR` | 否 | `./output` | 生成图片输出目录 |

## API 接口

后端启动后可通过 Swagger UI 查看完整接口文档：`http://localhost:8000/docs`

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/health` | 健康检查 |
| `GET` | `/api/v1/health/ready` | 服务就绪检查（含 AK/SK 校验） |
| `POST` | `/api/v1/generations/text2img` | 提交文生图任务 |
| `POST` | `/api/v1/generations/img2img` | 提交图生图任务 |
| `POST` | `/api/v1/generations/inpainting` | 提交局部重绘任务 |
| `GET` | `/api/v1/generations/{id}` | 获取生成结果详情 |
| `GET` | `/api/v1/generations/{id}/status` | 查询任务状态 |
| `GET` | `/api/v1/generations` | 查询历史记录列表 |
| `DELETE` | `/api/v1/generations/{id}` | 删除历史记录 |
| `POST` | `/api/v1/upload/image` | 上传图片文件 |

## 使用指南

1. 启动后端和前端服务后，浏览器访问 `http://localhost:5173`
2. **文生图**：输入正向/负面提示词，选择尺寸、风格等参数，点击生成
3. **图生图**：上传参考图片 + 输入提示词，点击生成
4. **局部重绘**：上传图片 → 画笔标记修改区域 → 输入描述 → 开始重绘
5. **历史记录**：查看所有生成记录，支持详情查看和删除

## 参考文档

- [即梦AI-图片生成4.6 接口文档](https://www.volcengine.com/docs/85621/2275082?lang=zh)
- [火山引擎控制台](https://console.volcengine.com)

## 许可证

仅供学习和参考使用。
