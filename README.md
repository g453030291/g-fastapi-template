# G FastAPI Template

一个专为**生产效率**打造的 FastAPI 后端模板，采用 **"异步 Web 框架 + 同步数据库"** 的混合架构。

**设计目标**：架构极简、依赖稳健、AI 友好（便于 AI 辅助开发）。

## 核心技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| Web 框架 | FastAPI (Async) | 高性能异步框架 |
| ORM | SQLModel + PyMySQL | **同步模式** |
| 配置管理 | Pydantic Settings V2 | 类型安全的配置 |
| 日志 | Loguru | 全面接管日志 |
| 定时任务 | APScheduler | 后台线程池执行 |
| AI 客户端 | OpenAI | 双模式 (Sync/Async) |

## 架构设计

### 混合模式核心理念

本项目**刻意选择同步数据库驱动**，而非全异步方案。原因：

1. **稳定性**：PyMySQL 成熟稳定，避免 aiomysql 等异步驱动的潜在坑
2. **简化心智**：Service 层全同步，无需处理异步上下文传递
3. **兼容性**：定时任务、后台任务天然适配同步模式

FastAPI 会自动将同步端点放入线程池执行，不会阻塞 Event Loop。

### 目录结构

```
app/
├── api/                  # 路由层 (Controllers)
│   └── ...               # 请求解析、参数校验、调用 Service
│
├── services/             # 业务逻辑层
│   └── ...               # 纯同步 Python 代码 (def)
│
├── core/                 # 基础设施
│   ├── config.py         # Pydantic Settings 配置
│   ├── database.py       # 同步数据库引擎和会话
│   ├── logger.py         # Loguru 配置
│   ├── scheduler.py      # APScheduler 定时任务
│   └── exceptions.py     # 全局异常处理
│
├── models/               # 数据模型
│   ├── response.py       # 统一响应封装
│   └── xxx.py            # SQLModel 表定义 + Pydantic Schema
│
├── client/               # 外部客户端
│   └── openai_client.py  # 单例模式，支持同步/异步双模式
│
├── utils/                # 工具函数
│   └── cache_util.py     # 线程安全缓存
│
└── main.py               # 应用入口
```

### 关键设计决策

#### 1. 同步/异步分层规则

| 层级 | 函数类型 | 原因 |
|------|----------|------|
| API 路由 (涉及 DB) | `def` | FastAPI 自动线程池化 |
| API 路由 (纯 I/O) | `async def` | 非阻塞 |
| Service 层 | `def` | 与同步 DB 兼容 |
| 定时任务 | `def` | 后台线程执行 |

#### 2. OpenAI 双模式客户端

```python
# 路由层 (async) - 使用异步方法
await openai_client.chat_async(prompt)

# Service/定时任务 (sync) - 使用同步方法
openai_client.chat_sync(prompt)
```

#### 3. 统一响应格式

所有 API 必须使用 `Response` 类封装返回值：

```python
from app.models.response import Response

return Response.success(data=result)
return Response.fail(msg="Not found", code=404)
```

## 快速开始

### 环境准备

```bash
# 克隆项目
git clone <repo>
cd g-fastapi-template

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 修改数据库连接等配置
```

### 启动服务

```bash
# 开发模式
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 部署

```bash
docker build -t g-fastapi-template .
docker run -p 8000:8000 --env-file .env g-fastapi-template
```

## 开发规范

详细的架构规则和编码规范请参阅 [CONTRIBUTING.md](./CONTRIBUTING.md)。

**核心铁律**：

1. **数据库操作必须同步** - Service 层函数用 `def`，禁止 `async def`
2. **禁止 print** - 统一使用 `loguru` 的 `logger`
3. **统一响应格式** - 所有 API 返回 `Response.success()` 或 `Response.fail()`

## License

MIT
