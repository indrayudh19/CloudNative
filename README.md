# Library Management System (LMS)

A complete, modern, microservice-based Library Management System built with **Python**, **FastAPI**, **SQLite (SQLAlchemy)**, and **Streamlit**.

---

## 🌟 Key Features

- **Role-Based Access Control**:
  - **Administrator**: Book management, member status control, issuing and returning books, automatic overdue fine calculations, fine/payment tracking, transaction monitoring, and interactive Plotly analytics.
  - **Member**: Live catalog browsing with real-time stock, personal borrowing history, fine balance inspection, and simulated fine payments with instant transaction references.
- **Microservices Architecture**:
  - **User Service** (`http://localhost:8001`): Member registration, auto ID generation (`MEM0001`...), login & profiles.
  - **Book Service** (`http://localhost:8002`): Catalog management, stock tracking, and soft-delete archive protection.
  - **Issue Service** (`http://localhost:8003`): Book issuance, eligibility verification (borrowing limits & outstanding fine checks), returns, and overdue fine generation.
  - **Payment Service** (`http://localhost:8004`): Fine payment processing (full/partial), transaction reference generation, and receipts.
  - **Admin Service** (`http://localhost:8005`): Aggregated statistics, analytics timelines, and audit logs.
- **Relational SQLite Database with Enforced Foreign Keys**:
  - `users`, `books`, `issues`, `fines`, `payments`, `audit_logs`.
  - Atomic transactions ensure inventory consistency.

---

## 🚀 Getting Started

### 1. Requirements

Install dependencies from `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 2. Initialize and Seed Database

Run the idempotent database initialization and seeding script:
```powershell
python -m database.init_db
python -m database.seed_data
```

This creates the database tables in `database/lms.db` and populates:
- Fixed administrator: `ADMIN001`
- 10 sample members: `MEM0001` to `MEM0010`
- 15 classic and tech books
- Initial demonstration transactions, overdue issues, and paid fines

### 3. Run Application

#### Option A: One-Click Startup Script (Recommended)
```powershell
python run_all.py
```
or on Windows PowerShell:
```powershell
.\start_services.ps1
```

#### Option B: Manual Service Startup
Start each microservice in separate terminal windows:
```powershell
python -m uvicorn services.userservice.main:app --port 8001
python -m uvicorn services.bookservice.main:app --port 8002
python -m uvicorn services.issueservice.main:app --port 8003
python -m uvicorn services.paymentservice.main:app --port 8004
python -m uvicorn services.adminservice.main:app --port 8005
```

Then run the Streamlit frontend:
```powershell
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🔑 Login Credentials

| Role | User ID | Password | Notes |
|---|---|---|---|
| **Admin** | `ADMIN001` | *Any non-empty* | Full admin dashboard & controls |
| **Member** | `MEM0001` ... `MEM0010` | *Any non-empty* | Sample members |
| **New Member** | Auto-generated (e.g. `MEM0011`) | *Any non-empty* | Register via New User form |

---

## 📑 Interactive API Documentation (Swagger)

- User Service: [http://localhost:8001/docs](http://localhost:8001/docs)
- Book Service: [http://localhost:8002/docs](http://localhost:8002/docs)
- Issue Service: [http://localhost:8003/docs](http://localhost:8003/docs)
- Payment Service: [http://localhost:8004/docs](http://localhost:8004/docs)
- Admin Service: [http://localhost:8005/docs](http://localhost:8005/docs)

