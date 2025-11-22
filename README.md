# G FastAPI Template (Sync DB Edition)

这是一个专为**生产效率**打造的 FastAPI 后端模板。
特点：**架构极简**、**依赖稳健**、**AI 友好**。

## 🏗️ 核心架构 (Critical)

本项目采用 **"异步 Web 框架 + 同步数据库"** 的混合模式，请务必遵守：

- **Framework**: FastAPI (Async)
- **Database**: SQLModel + PyMySQL (**Sync Mode**)
- **Scheduler**: APScheduler (BackgroundScheduler / Threaded)
- **Config**: Pydantic Settings V2
- **Logging**: Loguru (全面接管)

### 🚨 开发铁律
1. **数据库操作**：在 Service/API 层操作数据库时，必须使用 **`def`** (同步函数)，**严禁**使用 `async def`，否则会阻塞 Event Loop。
2. **外部请求**：router 中使用 async def,service 层使用 def。
3. **定时任务**：任务函数必须是同步的 `def`，由后台线程池执行。

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repo>
cd g-fastapi-template

# 复制配置
cp .env.example .env
# (手动修改 .env 里的数据库配置)