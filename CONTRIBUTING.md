# Contributing & Architecture Guide

> **ATTENTION AI ASSISTANTS (Cursor, Copilot, Claude, etc.)**:
> Before generating any code, you **MUST** read and strictly follow the architecture rules defined below.
> This project uses a specific **"Sync DB + Async Framework"** hybrid architecture. Do NOT apply generic fully-async FastAPI patterns blindly.

---

## 1. Core Tech Stack

- **Web Framework**: FastAPI (Async)
- **ORM**: SQLModel (SQLAlchemy Core)
- **Database Driver**: PyMySQL (**Sync Mode**)
- **Configuration**: Pydantic Settings V2
- **Logging**: Loguru (Replaces standard logging)
- **External Clients**: OpenAI (Dual-mode: Sync/Async)

---

## 2. Critical Architecture Rules

### 2.1 Database Interaction (Sync Mode)
This project uses a **synchronous** database driver (PyMySQL).

- **STRICTLY FORBIDDEN**:
  - NEVER use `await` for database operations (e.g., `await session.exec(...)`).
  - NEVER define Service layer functions involving DB operations as `async def`.

- **MUST DO**:
  - **Service Layer**: All functions must be defined with **`def`** (Synchronous).
  - **API Routes**: If an endpoint directly depends on the database `session`, define it with **`def`**. FastAPI will automatically run it in a thread pool to avoid blocking the Event Loop.
  - **Dependency Injection**: Use `def get_db()` which yields a sync session.

### 2.2 External API Calls (OpenAI/HTTP)
To balance high concurrency (API layer) and compatibility (Task layer), external clients support dual modes.

- **Scenario A: Inside API Routes (Routers)**
  - **Rule**: Use `async def` for the route.
  - **Action**: Call `await openai_client.chat_async(...)`.
  - **Reason**: Non-blocking I/O to release the Event Loop.

- **Scenario B: Inside Services or Scheduled Tasks**
  - **Rule**: The function itself is `def` (Sync).
  - **Action**: Call `openai_client.chat_sync(...)`.
  - **Reason**: Compatibility with the sync database context and background threads.

---

## 3. Directory Structure & Responsibilities

Follow this structure strictly. Do not place business logic in the API layer.

```
app/
|-- api/                  # Controllers / Routes
|   |-- ...               # Request parsing, Validation, Calling Services
|                         # NO complex business logic here.
|
|-- services/             # Business Logic Layer
|   |-- ...               # Pure synchronous Python code (def).
|                         # Handles atomic DB operations and complex logic.
|
|-- core/                 # Infrastructure
|   |-- config.py         # Pydantic Settings
|   |-- database.py       # DB Engine, Session, get_db (Sync)
|   |-- logger.py         # Loguru configuration
|
|-- models/               # Data Models
|   |-- response.py       # Uniform Response Wrapper (Response class)
|   |-- xxx.py            # SQLModel DB Tables (table=True) + Pydantic Schemas
|
|-- client/               # External Clients
|   |-- openai_client.py  # Singleton, Dual-mode (Sync/Async) wrapper
|
|-- utils/                # Utilities
    |-- cache_util.py     # Thread-safe caching tools
```

---

## 4. Coding Standards

### 4.1 Unified Response Format

All API endpoints **MUST** return data using the unified `Response` class.

**Import Path**:

```python
from app.models.response import Response
```

**Usage Patterns**:

```python
# Success Scenario
return Response.success(data=val)

# Error Scenario
return Response.fail(msg="Resource not found", code=404)
```

**Example in Router**:

```python
@router.get("/db")
def test_db_connection(session: Session = Depends(get_db)):
    result = session.exec(text("SELECT 1")).first()
    val = result[0] if result else 0
    return Response.success(data=val)
```

### 4.2 Logging

- **FORBIDDEN**: `print(...)` or `logging.info(...)`.
- **REQUIRED**: Use `loguru`.

```python
from loguru import logger

logger.info("Processing started")
logger.error(f"Error occurred: {e}")
```

### 4.3 Database Management

- **No Migrations**: Do not generate Alembic migration files.
- **Schema Management**: Database tables should be managed manually (e.g., using `SQLModel.metadata.create_all()` in your initialization code).

### 4.4 Type Hinting

- All functions must use Python type hints.
- Use `str | None` instead of `Optional[str]` (Python 3.10+ style).

```python
def get_user(user_id: int) -> User | None:
    ...
```
