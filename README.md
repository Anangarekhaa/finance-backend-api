# 💰 Finance Dashboard API

A role-based finance data management backend built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy** — designed to serve a multi-user finance dashboard with clean access control, aggregated analytics, and production-ready structure.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [Role-Based Access Control](#role-based-access-control)
- [API Endpoints](#api-endpoints)
- [Setup & Installation](#setup--installation)
- [Running with Docker](#running-with-docker)
- [Running Tests](#running-tests)
- [Assumptions & Design Decisions](#assumptions--design-decisions)

---

## Overview

This backend powers a **shared organisation-wide finance dashboard** where all users operate on the same pool of financial records. Access is controlled by role-based permissions rather than data ownership

| Role | Capabilities |
|---|---|
| **Viewer** | Dashboard summary only |
| **Analyst** | Records (with filters + search) + full dashboard |
| **Admin** | Full CRUD on records + user management + full dashboard |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Auth | JWT (via `python-jose`) |
| Validation | Pydantic v2 |
| Password Hashing | bcrypt (via `passlib`) |
| Containerization | Docker + Docker Compose |
| Testing | Pytest + FastAPI TestClient |

---

## Project Structure

```
finance-backend/
├── app/
│   ├── main.py              ← FastAPI app init + lifespan
│   ├── database.py          ← SQLAlchemy engine + session
│   ├── models.py            ← User + FinancialRecord models
│   ├── schemas.py           ← Pydantic request/response schemas
│   ├── dependencies.py      ← get_current_user + require_role
│   ├── enums.py             ← Role + TransactionType enums
│   ├── routers/
│   │   ├── auth.py          ← POST /auth/login
│   │   ├── users.py         ← User management (admin only)
│   │   ├── records.py       ← Financial records CRUD + filters
│   │   └── dashboard.py     ← Summary + trends analytics
│   └── core/
│       └── config.py        ← Environment config via pydantic-settings
├── tests/
│   └── test_api.py          ← Full test suite (auth, users, records, dashboard)
├── seed.py                  ← DB seed script with sample data
├── requirements.txt
├── .env
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Data Models

### User

| Field | Type | Notes |
|---|---|---|
| `id` | Integer (PK) | Auto-increment |
| `name` | String | Required |
| `email` | String | Unique |
| `password_hash` | String | bcrypt hashed |
| `role` | Enum | viewer / analyst / admin |
| `is_active` | Boolean | Default: true |
| `created_at` | Timestamp | Auto |

### FinancialRecord

| Field | Type | Notes |
|---|---|---|
| `id` | Integer (PK) | Auto-increment |
| `amount` | Numeric(10,2) | Must be > 0 |
| `type` | Enum | income / expense |
| `category` | String | Indexed |
| `date` | Date | Indexed |
| `notes` | String | Optional |
| `created_by` | FK → User.id | Audit trail, not ownership |
| `is_deleted` | Boolean | Soft delete flag |
| `created_at` | Timestamp | Auto |
| `updated_at` | Timestamp | Auto on update |

> **Note:** `created_by` is an audit field — it records who created the entry. Records are organisation-wide, not user-owned.

---

## Role-Based Access Control

RBAC is implemented using **FastAPI dependency injection** — clean, reusable, and enforced at the API layer before any business logic runs.

```
Request → HTTPBearer (verify JWT) → get_current_user → require_role → endpoint
```

```python
# Usage on any endpoint
Depends(require_role([Role.admin, Role.analyst]))
```

### Permission Matrix

| Endpoint | Viewer | Analyst | Admin |
|---|---|---|---|
| `POST /auth/login` | ✅ | ✅ | ✅ |
| `GET /dashboard/summary` | ✅ | ✅ | ✅ |
| `GET /dashboard/trends` | ❌ | ✅ | ✅ |
| `GET /records/` (no filters) | ❌ | ✅ | ✅ |
| `GET /records/` (with filters) | ❌ | ✅ | ✅ |
| `GET /records/{id}` | ❌ | ✅ | ✅ |
| `POST /records/` | ❌ | ❌ | ✅ |
| `PATCH /records/{id}` | ❌ | ❌ | ✅ |
| `DELETE /records/{id}` | ❌ | ❌ | ✅ |
| `GET /users/` | ❌ | ❌ | ✅ |
| `POST /users/` | ❌ | ❌ | ✅ |
| `PATCH /users/{id}` | ❌ | ❌ | ✅ |
| `DELETE /users/{id}` | ❌ | ❌ | ✅ |

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/login` | Login with email + password → returns JWT |

### Users (Admin only)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/users/` | Create a new user with role |
| GET | `/users/` | List users (search by name/email, filter by role/status) |
| PATCH | `/users/{id}` | Update role or active status |
| DELETE | `/users/{id}` | Hard delete user |

### Financial Records
| Method | Endpoint | Description |
|---|---|---|
| GET | `/records/` | List records with optional filters + pagination |
| GET | `/records/{id}` | Get single record by ID |
| POST | `/records/` | Create record (admin only) |
| PATCH | `/records/{id}` | Update record (admin only) |
| DELETE | `/records/{id}` | Soft delete record (admin only) |

**Filter/search query params (analyst + admin):**
```
?type=income
&category=food
&start_date=2024-01-01
&end_date=2024-12-31
&search=alice          ← searches creator name/email (ILIKE)
&page=1
&limit=10
```

### Dashboard
| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/summary` | Total income, expenses, net balance, category breakdown, recent activity |
| GET | `/dashboard/trends?period=monthly` | Monthly or weekly income vs expense trends (analyst + admin) |

**Sample summary response:**
```json
{
  "total_income": 358000,
  "total_expenses": 161600,
  "net_balance": 196400,
  "category_breakdown": {
    "salary": 300000,
    "rent": 90000,
    "food": 46000
  },
  "recent_activity": [...]
}
```

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL running locally

### Steps

```bash
# 1. clone the repo
git clone <repo-url>
cd finance-backend

# 2. create and activate virtual environment
python -m venv venv
source venv/bin/activate        # windows: venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt

# 4. create .env file
cp .env.example .env            # then fill in your values

# 5. create the database
psql -U postgres -c "CREATE DATABASE financedb;"

# 6. run migrations
alembic upgrade head

# 7. seed sample data (optional but recommended)
python -m seed

# 8. start the server
uvicorn app.main:app --reload
```

### Environment Variables (`.env`)


An `.env.example` file is included with all required environment variables.


```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/financedb
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### API Docs

Once running, interactive docs are available at:
- Swagger UI → `http://localhost:8000/docs`
- ReDoc → `http://localhost:8000/redoc`

---

## Running with Docker

```bash
# build and start all services
docker-compose up --build

# seed the database (run after containers are up)
docker exec -it finance_backend python -m seed
```

This starts two services:
- `db` → PostgreSQL 15 on port 5432
- `api` → FastAPI app on port 8000

Migrations run automatically on API startup via `alembic upgrade head`.

---

## Running Tests

Tests use a **separate Postgres test database** (`financedb_test`) to keep test data isolated from development data.

```bash
# create test database first
psql -U postgres -c "CREATE DATABASE financedb_test;"

# run tests
pytest tests/test_api.py -v
```

**Test coverage includes:**
- Auth — login success, wrong password, inactive user blocked
- Users — admin CRUD, role/status updates, search by name/email
- Records — role-based access, filters, search, soft delete, pagination
- Dashboard — summary values, trends access per role
- Validation — negative amount, invalid type, missing fields → 422

---

## Seed Data

A seed script is provided to populate sample users and financial records for testing and demonstration, creating 5 users and 35 financial records spanning 6 months across realistic categories.


---

## Assumptions & Design Decisions

### Shared Data Model
Records are **organisation-wide**, not user-owned. All authorised users see the same financial data. `created_by` is an audit trail field (who entered it), not an ownership field. This reflects real-world finance dashboards where data belongs to the organisation.

### Role Assignment
Users cannot self-register. Only an admin can create users and assign roles. This is intentional — an internal finance dashboard is not a public-facing app.

### Soft Delete for Records
Financial records use soft delete (`is_deleted = true`) so data is never truly lost — important for audit trails in financial systems. Users are hard-deleted since they have no financial audit significance on their own.

### Summary Computed On-Demand
Dashboard summary and trends are computed via SQL aggregations on every request. No caching layer is added — this is a deliberate simplicity tradeoff acceptable for this scale. A production system would add Redis caching.

### JWT Contains Role
The user's role is embedded in the JWT payload at login time. This avoids an extra database call on every authenticated request to check the role.

### Viewer Access
Viewers have access only to `GET /dashboard/summary`. They cannot list, filter, search, or view individual records. Their role is purely observational at the summary level.

### Pagination
All record listing endpoints support pagination via `?page=` and `?limit=` query params. Default is 10 records per page, max 100.

### Database Indexes
Indexes are added on `category`, `date`, `created_by`, and a composite index on `(type, category)` and `(date, is_deleted)` to optimise the most common query patterns (filtering by type+category, date range queries with soft delete filter).


## Security Considerations

- SQL injection prevention via ORM (SQLAlchemy parameterized queries)
- JWT-based authentication
- Role-based authorization (RBAC)
- Input validation using Pydantic
- Proper HTTP status codes and error handling