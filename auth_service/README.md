# Auth Service

A production-ready Authentication and Profiling microservice. Built with **FastAPI**, **PostgreSQL**, and **Redis**. Features robust asynchronous processing, JWT-based sessions, role-ready architecture, email dispatching, Google OAuth integration, and full industrial-grade Redis caching.

## Features

- **Authentication Flows**: Email/Password Registration and Login, Google OAuth integration.
- **Session Management**: JWT `access_token` and `refresh_token` architecture. Stateful Redis-backed blacklist to invalidate sessions globally (`/logout-all`).
- **Security & Reliability**: 
  - Password Hashing (bcrypt).
  - Account Lockout mechanism (mitigates brute force).
  - Real-time Redis-backed `Status` checks (disables active tokens automatically if a user is Banned/Deactivated).
- **OTP Verification**: Email verification and "Forgot Password" workflows powered by secure DB-tracked short-lived OTPs.
- **Caching Engine**: Redis is deeply integrated. User data and session statuses are cached to avoid unnecessary database trips on highly concurrent protected endpoints.
- **Auditing & Analytics**: Embedded telemetry logs events (`LOGOUT`, `LOGIN`, `PASSWORD_CHANGE`) with IP and User-Agent tracking for threat intelligence.
- **Docker-First Environment**: Hot-reloading Docker compose stack. No local pycache clutter.

---

## Architecture & Technologies

- **Web Framework**: FastAPI (Async)
- **Database**: PostgreSQL 15, managed with SQLAlchemy (Asyncpg driver) and Alembic (Migrations).
- **Cache**: Redis
- **Containerization**: Docker & Docker Compose
- **Configuration**: Pydantic Settings
- **Email**: SMTP integration

---

## Folder Structure

```
.
├── alembic/                # Database migrations logic and history
├── app/                    # Primary application package
│   ├── api/                # Application API
│   │   └── v1/             # Versioned API routes
│   │       ├── auth/       # Authentication routes (local, session, social)
│   │       └── user/       # User profiles and management
│   ├── core/               # System configs, OAuth, Redis clients, Security dependencies
│   ├── database/           # Database configurations and connection utilities
│   ├── models/             # SQLAlchemy ORM models (Modularized)
│   ├── repository/         # DB Abstraction layer for clean data access
│   ├── schemas/            # Pydantic validation schemas (Models for requests/responses)
│   ├── services/           # Core Business Logic (AuthService, UserService, OTPService, AnalyticsService)
│   ├── utils/              # Helper utilities (e.g. Email dispatch)
│   └── main.py             # FastAPI entry point, lifecycle events, and Global Exception handlers
├── docker-compose.yml      # Container orchestration
├── Dockerfile              # App container build definition
└── alembic.ini             # Alembic migration config
```

---

## Environment Setup (`.env`)

You must construct a `.env` file at the root of the project to configure dependencies. A sample template is provided below. 

> **Important**: When running in `docker-compose`, ensure your `DATABASE_URL` target is `db` and `REDIS_URL` target is `redis` (as these reflect container network hostnames).

```ini
# App Settings
PROJECT_NAME="Auth Service"
ENVIRONMENT=development
DEBUG=True

# Database (PostgreSQL URL)
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/investcode

# Redis Connection
REDIS_URL=redis://redis:6379/0

# Security (Crucial for Session stability!)
# Use openssl rand -hex 32 to generate
SECRET_KEY=your-super-long-random-secret-key-change-it
SESSION_SECRET=your-random-session-secret-change-it
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# SMTP (Transactional Emails -> Forgot Password, Verification)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-service-account@gmail.com
EMAIL_PASSWORD=your-app-password

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Frontend Integration
FRONTEND_URL=http://localhost:3000
```

---

## Running the Project

This project adopts a **Container-Only Workflow**. This means you do not need to manage virtual environments (`venv`) on your host machine.

### 1. Build and Start Services
Run the following in the root directory. This will boot PostgreSQL, Redis, and the FastAPI application simultaneously.

```bash
docker-compose up --build
```
*The app directory is mounted as a volume `/app` in the container, meaning any code modifications will trigger a live reload in development mode.*

### 2. Verify Health
Open your browser or hit the health-check endpoint:
`GET http://localhost:8000/health`
This will ping the DB, Redis, and SMTP server to confirm deep initialization.

### 3. Swagger UI Documentation
Navigate to `http://localhost:8000/docs` to see the generated interactive API schema.

---

## Database Migrations (Alembic)

Alembic manages database schema versions. Since the app is dockerized, you should run Alembic commands *inside* the running application container.

**Generate a new migration** (If you modify the ORM models in `app/models/`):
```bash
docker-compose exec auth_service alembic revision --autogenerate -m "describe_your_changes"
```

**Apply migrations to the DB**:
```bash
docker-compose exec auth_service alembic upgrade head
```

---

## Troubleshooting

- **Database Errors on Startup**: Ensure Alembic migrations have been applied. Sometimes new environments require an initial `alembic upgrade head`.
- **Email Failed to Send**: Double check your `EMAIL_PASSWORD`. If using Gmail, it requires an **App Password**, not your primary login password.
- **Cache Eviction**: You can forcefully purge local cache state via terminal: `docker-compose exec redis redis-cli flushall`.
