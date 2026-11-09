# Global Configuration for Library Management System (LMS)
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Authentication / Defaults
ADMIN_ID = "ADMIN001"
MAX_BOOKS_PER_MEMBER = 3
LOAN_PERIOD_DAYS = 14
FINE_PER_DAY = 5.0

# Database
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATABASE_DIR / "lms.db"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# Microservices Ports & URLs
SERVICE_PORTS = {
    "user": 8001,
    "book": 8002,
    "issue": 8003,
    "payment": 8004,
    "admin": 8005,
}

SERVICE_URLS = {
    "user": f"http://127.0.0.1:{SERVICE_PORTS['user']}",
    "book": f"http://127.0.0.1:{SERVICE_PORTS['book']}",
    "issue": f"http://127.0.0.1:{SERVICE_PORTS['issue']}",
    "payment": f"http://127.0.0.1:{SERVICE_PORTS['payment']}",
    "admin": f"http://127.0.0.1:{SERVICE_PORTS['admin']}",
}

