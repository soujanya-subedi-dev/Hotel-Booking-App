# Hotel Booking App — Local Setup

End-to-end hotel booking demo
**Stack:** React (Vite) + Flask + PostgreSQL

---

## Prerequisites

* **Python 3.11+**
* **Node.js 18+** (includes npm)
* **PostgreSQL 14+**

---

## 1) Backend setup (Windows / PowerShell)

```powershell
cd backend

# (First time) create & activate venv
python -m venv venv
venv\Scripts\activate

# Install deps
pip install -r requirements.txt
```

### 1.1 Configure environment

Create `backend/.env`:

```
FLASK_APP=wsgi:app
FLASK_ENV=development
DATABASE_URL=postgresql+psycopg2://hoteluser:hotelpw@localhost:5432/hotel_db
JWT_SECRET_KEY=change-me-in-prod
```

### 1.2 Create PostgreSQL role & database

Open **psql** as `postgres` (superuser):

```powershell
psql -U postgres -h localhost -W
```

In psql:

```sql
-- Create app role (can create db)
CREATE ROLE hoteluser LOGIN PASSWORD 'hotelpw' CREATEDB;

-- Create database owned by hoteluser
CREATE DATABASE hotel_db OWNER hoteluser;

-- Add extensions (superuser)
\c hotel_db
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS btree_gist;
\q
```

### 1.3 Migrate & (optional) seed

```powershell
# Back in backend venv
flask db upgrade

# (Optional) seed demo data: users, 5 hotels, room types, rooms, sample booking
python -m scripts.seed
```

### 1.4 Run the API

```powershell
flask run --port 5000
```

API will be at: `http://127.0.0.1:5000/api`

**Seeded logins:**

* Admin: `admin@example.com / admin123`
* User:  `user@example.com / user123`

---

## 2) Frontend setup (Terminal 2)

```powershell
cd frontend
npm install
```

Create `frontend/.env` (optional; defaults to 5000):

```
VITE_API_BASE_URL=http://127.0.0.1:5000/api
```

Run the dev server:

```powershell
npm run dev
```

App opens at Vite’s URL (e.g. `http://127.0.0.1:5173`).

---

## 3) Common flows to test

* **Browse**: Home → click a hotel → pick dates → **Check Availability** → **Book Now**.
* **Auth**: Login/Register (JWT stored in localStorage).
* **My Bookings**: view & cancel.
* **Admin**: Login as admin → `/admin`

  * Create/Manage hotels, room types, rooms.
  * Add hotel images (URLs).
  * View occupancy & per-hotel user bookings.

---

## 4) Notes & Tips

* If DB connection fails, confirm:

  * PostgreSQL running on `localhost:5432`
  * `DATABASE_URL` matches your role/password/database
* If migrations complain about permissions, ensure extensions were created as superuser.
* CORS is enabled server-side. If you prefer proxying, you can add to `frontend/vite.config.js`:

  ```js
  server: { proxy: { '/api': 'http://127.0.0.1:5000' } }
  ```
* Re-seeding may add duplicate hotels; users are upserted.

---

## 5) Scripts (quick reference)

Backend:

```powershell
cd backend
venv\Scripts\activate
flask db upgrade
python -m scripts.seed     # optional
flask run --port 5000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

That’s it—happy hacking!
