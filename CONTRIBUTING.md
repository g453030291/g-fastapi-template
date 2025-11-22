# 贡献指南与开发规范

欢迎参与开发！为了保持项目架构的整洁和高效，请所有开发者（包括 AI 助手）严格遵守以下规范。

## 🏗️ 核心技术栈
- **框架**: FastAPI (异步)
- **数据库**: SQLModel + PyMySQL (同步模式)
- **定时任务**: APScheduler (BackgroundScheduler)
- **配置**: Pydantic Settings V2

## 🚨 关键架构原则 (非常重要)

### 1. 数据库交互 (同步 vs 异步)
本项目采用了 **"异步 Web 框架 + 同步数据库"** 的混合模式：
- **❌ 严禁**: 在数据库操作中使用 `await` (如 `await session.exec(...)`)。
- **✅ 必须**: Service 层和 Repository 层操作数据库时，使用普通 `def` 函数。
- **✅ 必须**: FastAPI 路由函数如果依赖数据库，必须使用 `def` 定义 (让 FastAPI 放入线程池运行)。
    ```python
    # 正确示例
    @router.get("/users")
    def get_users(db: Session = Depends(get_db)): # 注意是 def
        return db.exec(select(User)).all()
    ```

### 2. 目录职责
- `app/api/`: **只做** 请求接收、参数校验、响应转换。**禁止** 写复杂业务逻辑。
- `app/services/`: 承载所有业务逻辑。
- `app/core/`: 基础设施配置 (Config, Log, DB)。
- `app/client/`: 第三方 API 客户端 (OpenAI 等) 必须单例封装。

### 3. 代码风格
- **日志**: 必须使用 `from loguru import logger`，禁止使用 `print`。
- **工具**: 优先使用 `app/utils/` 下的现成工具 (如 `cache_util`)。
- **模型**: SQLModel 请务必加上 `table=True`。

## 🤖 给 AI 助手的指令
如果你是 Cursor、Copilot 或其他 AI 助手，在生成代码前，请务必：
1. 检查是否违反了上述“同步数据库”规则。
2. 检查是否遵循了目录分层结构。