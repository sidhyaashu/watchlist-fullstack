# 🧠 Final Architecture (Your Case)

```text
Client
  ↓
API Gateway
  ↓
-----------------------------
| Auth Service              |
| Watchlist Service        |
-----------------------------
        ↓
PostgreSQL (shared or separate schemas)

Market Data Service → only writes to DB (offline ingestion)
```

---

# 🚀 FULL IMPLEMENTATION ROADMAP (PRODUCTION-GRADE)

Follow this **strict phase-by-phase plan** — don’t skip.

---

# 🟢 PHASE 0 — Foundation Setup

### 🎯 Goal:

Create a clean service skeleton

### ✅ Tasks:

* Create `watchlist_service/`
* Setup folder structure (what I gave earlier)
* Add FastAPI app

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Watchlist Service")

@app.get("/health")
def health():
    return {"status": "ok"}
```

---

# 🟢 PHASE 1 — Database Setup (CRITICAL)

### 🎯 Goal:

Connect PostgreSQL properly

### ✅ Tasks:

### 1. Setup config

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

settings = Settings()
```

---

### 2. Async DB Session

```python
# db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

---

### 3. Base Model

```python
# db/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

---

### 4. Alembic Setup

* `alembic init`
* Configure DB URL
* Enable async migrations

---

# 🟢 PHASE 2 — Models (Schema Design)

### 🎯 Goal:

Define DB structure

---

## ✅ Watchlist Model

```python
# models/watchlist.py
class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, nullable=False)
    name = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
```

---

## ✅ Watchlist Item Model

```python
# models/watchlist_item.py
class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(UUID, primary_key=True)
    watchlist_id = Column(UUID, ForeignKey("watchlists.id"))
    instrument_id = Column(String, nullable=False)
    symbol = Column(String)
    exchange = Column(String)
```

---

## ⚠️ Important

Add constraint:

```python
UniqueConstraint("watchlist_id", "instrument_id")
```

---

# 🟢 PHASE 3 — Schemas (Validation Layer)

### 🎯 Goal:

Define request/response

---

```python
# schemas/watchlist.py

class WatchlistCreate(BaseModel):
    name: str

class WatchlistResponse(BaseModel):
    id: UUID
    name: str
```

---

```python
# schemas/watchlist_item.py

class AddItemRequest(BaseModel):
    instrument_id: str
    symbol: str
    exchange: str
```

---

# 🟢 PHASE 4 — Repository Layer (DB Access)

### 🎯 Goal:

Isolate DB queries

---

```python
# repository/watchlist_repo.py

class WatchlistRepository:

    async def create(self, db, user_id, name):
        ...
    
    async def get_by_user(self, db, user_id):
        ...
```

---

```python
# repository/watchlist_item_repo.py

class WatchlistItemRepository:

    async def add_item(self, db, watchlist_id, data):
        ...
    
    async def remove_item(self, db, watchlist_id, instrument_id):
        ...
```

---

# 🟢 PHASE 5 — Service Layer (BUSINESS LOGIC)

### 🎯 Goal:

Handle real logic

---

```python
# services/watchlist_service.py

class WatchlistService:

    async def create_watchlist(self, db, user_id, name):
        # check limit
        # create
        ...
```

---

```python
# services/watchlist_item_service.py

class WatchlistItemService:

    async def add_item(self, db, user_id, watchlist_id, data):
        # validate ownership
        # add item
        ...
```

---

# 🟢 PHASE 6 — Auth Integration

### 🎯 Goal:

Extract user from JWT

---

```python
# api/deps.py

def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    # decode JWT
    return user_id
```

---

# 🟢 PHASE 7 — API Layer (Endpoints)

---

## Watchlist APIs

```python
POST   /watchlists
GET    /watchlists
DELETE /watchlists/{id}
```

---

## Items APIs

```python
POST   /watchlists/{id}/items
DELETE /watchlists/{id}/items/{instrument_id}
GET    /watchlists/{id}/items
```

---

# 🟢 PHASE 8 — Market Data Join (IMPORTANT CHANGE)

### 🎯 Since data is already in DB

👉 You will JOIN with instrument table

---

```sql
SELECT wi.*, i.name, i.last_price
FROM watchlist_items wi
JOIN instruments i
ON wi.instrument_id = i.id
```

---

👉 No API call needed — just DB query

---

# 🟢 PHASE 9 — API Gateway Integration

### 🎯 Goal:

Expose service

---

Add route:

```bash
/watchlists → watchlist_service
```

---

# 🟢 PHASE 10 — Docker Setup

### 🎯 Goal:

Run service independently

---

* Dockerfile
* docker-compose

Include:

* PostgreSQL
* watchlist_service

---

# 🟢 PHASE 11 — Redis (Optional but Recommended)

### 🎯 Goal:

Speed up reads

---

Cache:

```text
user_watchlist:{user_id}
```

---

# 🟢 PHASE 12 — Testing

### 🎯 Goal:

Production readiness

---

* Unit tests (services)
* API tests (endpoints)

---

# 🧠 KEY ARCHITECTURE DECISIONS (VERY IMPORTANT)

### ✅ Direct DB Read from Instruments

✔ Faster
✔ Simpler
✔ No network latency

---

### ❗ But Keep Loose Coupling

👉 Even if same DB:

* Treat instruments as external
* Don’t tightly couple models

---

# 🚨 Common Mistakes (Avoid)

❌ Mixing watchlist + market tables
❌ No ownership validation (user_id check)
❌ No unique constraint
❌ No indexing on user_id

---