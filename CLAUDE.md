# Architecture Guide

> **Before generating any code, you MUST read and strictly follow the rules below.**
> This project uses a **Full Async** architecture. Do NOT use sync database patterns.

---

## 1. Core Tech Stack

- **Web Framework**: FastAPI (Async)
- **ORM**: SQLModel (SQLAlchemy 2.0 Core)
- **Database Driver**: asyncpg (**Async Mode**)
- **Configuration**: Pydantic Settings V2
- **Logging**: Loguru (Replaces standard logging)
- **LLM Client**: LLMClient — supports OpenAI and Anthropic (configured via `LLM_PROVIDER`)
- **HTTP Client**: httpx (Async)

---

## 2. Critical Architecture Rules

### 2.1 Database Interaction (Async Mode)

This project uses an **asynchronous** database driver (asyncpg).

- **STRICTLY FORBIDDEN**:
  - NEVER use sync `Session` for DB operations.
  - NEVER define Service or Route functions involving DB as plain `def` — must be `async def`.

- **MUST DO**:
  - **Service Layer**: All functions involving DB must be `async def`.
  - **API Routes**: Always `async def`. Use `AsyncSession` from dependency injection.
  - **Dependency Injection**: Use `async def get_db()` which yields an `AsyncSession`.
  - **DB Operations**: Always `await session.execute(...)` or `await session.exec(...)`.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db

@router.get("/example")
async def example(session: AsyncSession = Depends(get_db)):
    result = await session.execute(text("SELECT 1"))
    return Response.success(data=result.scalar())
```

### 2.2 LLM Client (OpenAI / Anthropic)

Switch providers via `LLM_PROVIDER` env var. Interface is identical regardless of provider.

- **In API Routes**: Use `await llm_client.chat_async(...)`.
- **In Services or Scheduled Tasks**: Use `llm_client.chat_sync(...)`.

```python
from app.client.llm_client import llm_client

# Async (in route)
result = await llm_client.chat_async(prompt="Hello", system_prompt="You are helpful.")

# Sync (in service / scheduler job)
result = llm_client.chat_sync(prompt="Hello")
```

Config for Claude (Anthropic):
```
LLM_PROVIDER=anthropic
LLM_API_KEY=your-anthropic-key
LLM_MODEL=claude-sonnet-4-6
```

Config for OpenAI:
```
LLM_PROVIDER=openai
LLM_API_KEY=your-openai-key
LLM_MODEL=gpt-4o-mini
```

### 2.3 HTTP Client (httpx)

Use `http_client` for all outbound HTTP calls.

```python
from app.client.http_client import http_client

response = await http_client.get("https://api.example.com/data")
data = response.json()
```

### 2.4 Scheduled Tasks

Use `AsyncIOScheduler`. Jobs can be `async def` and directly `await` DB or HTTP operations.

```python
from app.core.scheduler import get_scheduler

scheduler = get_scheduler()
scheduler.add_job(my_async_job, "cron", hour=9)
```

---

## 3. Directory Structure & Responsibilities

```
app/
|-- api/                  # Controllers / Routes
|   |-- ...               # async def routes. Request parsing, calling Services.
|                         # NO complex business logic here.
|
|-- services/             # Business Logic Layer
|   |-- ...               # async def functions.
|                         # Handles DB operations and complex logic.
|
|-- core/                 # Infrastructure
|   |-- config.py         # Pydantic Settings
|   |-- database.py       # Async Engine, AsyncSession, get_db
|   |-- logger.py         # Loguru configuration
|   |-- scheduler.py      # AsyncIOScheduler
|
|-- models/               # Data Models
|   |-- response.py       # Uniform Response Wrapper (Response class)
|   |-- xxx.py            # SQLModel DB Tables (table=True) + Pydantic Schemas
|
|-- client/               # External Clients
|   |-- llm_client.py     # Singleton, Dual-provider (OpenAI / Anthropic), Dual-mode (Sync/Async)
|   |-- http_client.py    # Singleton, Async httpx client with retry
|
|-- utils/                # Utilities
    |-- cache_util.py     # Thread-safe in-memory caching
```

---

## 4. Coding Standards

### 4.1 Unified Response Format

All API endpoints **MUST** return data using the unified `Response` class.

```python
from app.models.response import Response

# Success
return Response.success(data=val)

# Error
return Response.fail(msg="Resource not found", code=404)
```

### 4.2 Logging

- **FORBIDDEN**: `print(...)` or `logging.info(...)`.
- **REQUIRED**: Use `loguru`.

```python
from loguru import logger

logger.info("Processing started")
logger.error(f"Error occurred: {e}")
```

Each HTTP request automatically gets a `request_id` injected into the log context via middleware. All log lines within a request will include this ID.

### 4.3 Database Management

- **No Migrations**: Do not generate Alembic migration files.
- **Schema Management**: Use `SQLModel.metadata.create_all()` in initialization code.

### 4.4 Type Hinting

- All functions must use Python type hints.
- Use `str | None` instead of `Optional[str]` (Python 3.10+ style).

```python
async def get_user(user_id: int) -> User | None:
    ...
```
