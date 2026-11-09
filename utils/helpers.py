import re
import uuid
from datetime import datetime, date

def validate_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    cleaned = re.sub(r"[^\d]", "", phone)
    return len(cleaned) >= 7

def generate_transaction_ref(prefix: str = "TXN") -> str:
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

def format_currency(amount: float) -> str:
    return f"₹{amount:,.2f}"

def format_date(d) -> str:
    if isinstance(d, (datetime, date)):
        return d.strftime("%d %b %Y")
    return str(d) if d else "-"

