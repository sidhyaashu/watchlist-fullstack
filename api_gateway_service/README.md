# 📘 API Gateway — Detailed Functional & Non-Functional Specification

---

# 1. 🧩 System Overview

The API Gateway acts as the **single entry point** for all client requests and is responsible for:

* Request validation
* Authentication & identity propagation
* Intelligent routing
* Rate limiting & abuse protection
* Observability & logging
* AI-aware request handling (streaming + cost tracking)

---

# 2. ⚙️ Functional Requirements (Core Features)

---

## 2.1 🔐 Authentication & Identity Management

### 🎯 Objective

Ensure only **authorized and trusted traffic** reaches internal services.

---

### ✅ Supported Auth Methods

#### 1. JWT Authentication (Primary)

* Used by: Web & Mobile clients
* Source: `auth_service`

**Flow:**

1. Extract token from:

   ```
   Authorization: Bearer <token>
   ```
2. Decode locally using:

   * SECRET_KEY
   * ALGORITHM
3. Validate:

   * expiration (`exp`)
   * issuer (`iss`)
   * subject (`sub`)

---

#### 2. API Key Authentication

* Used by: External / enterprise clients

**Flow:**

1. Extract from:

   ```
   X-API-KEY: <key>
   ```

2. Lookup in:

   * Redis (fast path)
   * DB (fallback)

3. Validate:

   * active status
   * scopes (read/write/admin)

---

### 🔁 Identity Propagation

After validation, inject headers:

```
X-User-ID
X-Scopes
X-Auth-Type (JWT/API_KEY)
X-Request-ID
```

---

### ❌ Failure Cases

| Case            | Response |
| --------------- | -------- |
| Missing token   | 401      |
| Invalid token   | 401      |
| Expired token   | 401      |
| Invalid API key | 403      |

---

---

## 2.2 🔀 Intelligent Routing & Reverse Proxy

### 🎯 Objective

Forward requests to correct backend services dynamically.

---

### ✅ Routing Strategy

Use **Longest Prefix Match**

Example registry:

```python
ROUTES = {
    "/api/v1/news": "http://news_service:8001",
    "/api/v1/market": "http://market_service:8002",
}
```

---

### 🔁 Routing Flow

1. Extract request path
2. Resolve service using prefix matching
3. Strip prefix
4. Forward request

---

### 🔄 Path Transformation

| Incoming              | Forwarded |
| --------------------- | --------- |
| `/api/v1/news/latest` | `/latest` |
| `/api/v1/market/btc`  | `/btc`    |

---

### 📦 Payload Support

* JSON (large payloads)
* Multipart (file uploads)
* Query params preserved
* Headers forwarded

---

### ❌ Failure Cases

| Case              | Response |
| ----------------- | -------- |
| No matching route | 404      |
| Service down      | 502      |
| Timeout           | 504      |

---

---

## 2.3 ⚡ Rate Limiting

### 🎯 Objective

Prevent abuse and control usage cost (especially AI endpoints)

---

### ✅ Rate Limit Types

#### 1. Global (IP-based)

```
rate_limit:ip:<ip>
```

#### 2. User-based

```
rate_limit:user:<user_id>
```

#### 3. AI-specific

```
rate_limit:ai:<user_id>
```

---

### ⚙️ Algorithms

* Token Bucket (recommended)
  OR
* Sliding Window

---

### 📊 Example Limits

| Tier | Limit        |
| ---- | ------------ |
| Free | 100 req/min  |
| Pro  | 1000 req/min |
| AI   | 20 req/min   |

---

### ❌ Failure Response

```
429 Too Many Requests
Retry-After: <seconds>
```

---

---

## 2.4 🤖 AI-Aware Capabilities

---

### 🟢 1. Streaming Support

#### Protocols:

* SSE (`text/event-stream`)
* WebSockets

---

### 🔁 Behavior

* Do NOT buffer responses
* Stream chunk-by-chunk
* Preserve headers

---

---

### 🟡 2. LLM Usage Logging

Capture:

```
user_id
endpoint
model
tokens_used
latency
cost_estimate
```

Store in:

* DB OR
* Event queue (Kafka / Redis Stream)

---

---

### 🔴 3. AI Guardrails (Future)

**NOT in MVP**

Planned:

* PII detection
* Prompt filtering
* Output moderation

---

---

## 2.5 📊 Observability & Monitoring

---

### ✅ Request Tracking

Inject:

```
X-Request-ID (UUID)
```

---

### 📜 Logging

Log per request:

```
request_id
user_id
path
method
status_code
latency
service
```

---

### ❤️ Health Endpoints

```
GET /health
GET /ready
```

---

---

## 2.6 🔒 Security Features

---

### ✅ CORS

* Centralized control
* Allow specific origins

---

### ✅ IP Filtering

* Whitelist
* Blacklist

---

### ✅ Headers Protection

* Remove sensitive headers
* Add security headers

---

---

# 3. 🚀 Non-Functional Requirements

---

## 3.1 ⚡ Performance

| Metric           | Target            |
| ---------------- | ----------------- |
| Latency overhead | < 10ms            |
| P99 latency      | < 20ms            |
| Throughput       | 20k+ req/min/node |

---

## 3.2 📈 Scalability

---

### ✅ Architecture

* Stateless gateway
* External state:

  * Redis
  * DB

---

### ✅ Deployment

* Dockerized
* Horizontal scaling
* Kubernetes / Azure Container Apps

---

---

## 3.3 🔐 Security

---

* TLS termination via NGINX / Azure Gateway
* No direct service exposure
* Strict auth enforcement

---

---

## 3.4 📊 Reliability

| Metric           | Target            |
| ---------------- | ----------------- |
| Uptime           | ≥ 99.9%           |
| Failure Recovery | Automatic restart |

---

---

## 3.5 🧠 Maintainability

---

* Modular architecture
* Middleware-based design
* Config-driven routing

---

---

## 3.6 📡 Observability

---

### Metrics to Track:

* Request rate
* Error rate
* Latency
* Rate limit hits

---

---

# 4. 🧱 System Constraints

---

* Must be async (FastAPI / Starlette)
* Redis required for rate limiting
* JWT must be self-verifiable (no DB dependency)

---

---

# 5. 🧪 Edge Cases You MUST Handle

---

### 🔴 Auth Edge Cases

* Expired token
* Malformed JWT
* Missing API key

---

### 🔴 Routing Edge Cases

* Overlapping prefixes
* Trailing slashes

---

### 🔴 Rate Limiting Edge Cases

* Redis failure
* Burst traffic

---

### 🔴 Streaming Edge Cases

* Client disconnect
* Partial response

---

---

# 6. 🗺️ Phase Mapping (Build Order)

---

## ✅ Phase 1

* FastAPI app
* Basic proxy
* Static routing

---

## ✅ Phase 2

* JWT auth
* API keys

---

## ✅ Phase 3

* Redis rate limiting

---

## ✅ Phase 4

* Logging + request ID

---

## ✅ Phase 5

* Streaming + AI logging

---

---

# 7. 💡 Design Principles (VERY IMPORTANT)

---

### 1. Keep Gateway Thin

* No heavy business logic

---

### 2. Fail Fast

* Reject invalid requests early

---

### 3. Async Everywhere

* Avoid blocking calls

---

### 4. Extensible Design

* Future-ready (AI, policies, etc.)

---

---

# 🔚 Final Thought

This is no longer just:

> “API Gateway”

You are building:

> **AI Infrastructure Control Plane**

If you follow this doc strictly, you’ll end up with something **production-grade**, not just academic.