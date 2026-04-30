# InvestCode Platform — Root README

## Services
| Service | Port | Description |
|---------|------|-------------|
| NGINX (Edge) | `80` | Public entry point, reverse proxies to Gateway |
| API Gateway | internal | Routes all traffic, auth, rate limiting |
| Auth Service | internal | JWT, OAuth, session management |
| Client (Next.js) | `3000` | Web frontend |
| PostgreSQL | `5432` | Auth service database |
| Redis | `6379` | Rate limiting + session cache |

## Running the Full Stack

```bash
# From the root x/ directory
docker-compose up --build

# Or in detached mode
docker-compose up --build -d
```

## Service URLs

| Endpoint | Description |
|----------|-------------|
| `http://localhost:80/api/v1/health` | Gateway health check |
| `http://localhost:80/api/v1/auth/login` | Auth: Login |
| `http://localhost:80/api/v1/auth/signup` | Auth: Signup |
| `http://localhost:3000` | Next.js client |

## Stopping

```bash
docker-compose down

# Remove volumes too (wipes database)
docker-compose down -v
```

## Architecture

```
Client (3000) → NGINX (80) → API Gateway → Auth Service
                                         → News Service
                                         → Market Service
```
