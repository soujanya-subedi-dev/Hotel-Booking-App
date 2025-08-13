# Hotel Booking App – Backend (Flask)

Production-ready Flask backend for your Hotel Booking App.

## Quickstart

```bash
# 1) Python & dependencies
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) Environment
cp .env.example .env
# Edit .env -> set DATABASE_URL to your PostgreSQL DSN

# 3) Initialize DB (dev convenience: create tables from models)
flask --app run db init      # only the first time
flask --app run db migrate -m "init schema"
flask --app run db upgrade

# 4) Seed sample data
python scripts/seed.py

# 5) Run
python run.py
```

## Endpoints (high-level)

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/me` `PATCH /api/me` `PATCH /api/me/password`
- `GET /api/hotels` `GET /api/hotels/:id` `GET /api/hotels/:id/availability`
- `GET /api/bookings` `POST /api/bookings` `PATCH /api/bookings/:id/cancel`
- Admin: `GET /api/admin/users` `GET /api/admin/bookings` (JWT with role=admin)

## Notes

- Use PostgreSQL in production. The app reads `DATABASE_URL` and configures a safe connection pool.
- JWT identity is stored as string (compat with flask-jwt-extended best practices).
- CORS is restricted via `CORS_ORIGINS` (comma-separated).

## Deploying (Gunicorn example)

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app
```
