import requests
from config import SERVICE_URLS

class APIClient:
    def __init__(self, service_urls=None):
        self.urls = service_urls or SERVICE_URLS

    def _request(self, method: str, service: str, path: str, **kwargs):
        base_url = self.urls.get(service)
        if not base_url:
            return {"error": f"Unknown service {service}"}
        url = f"{base_url}{path}"
        try:
            resp = requests.request(method, url, timeout=10, **kwargs)
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            if resp.status_code >= 400:
                err_msg = data.get("detail", data.get("error", resp.text)) if isinstance(data, dict) else resp.text
                return {"error": err_msg, "status_code": resp.status_code}
            return data
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error to {service} service: {str(e)}"}

    # --- User Service ---
    def login(self, user_id: str, password: str = ""):
        return self._request("POST", "user", "/users/login", json={"user_id": user_id, "password": password})

    def register_member(self, data: dict):
        return self._request("POST", "user", "/users/register", json=data)

    def get_user(self, user_id: str):
        return self._request("GET", "user", f"/users/{user_id}")

    def get_users(self, role: str = None, search: str = None):
        params = {}
        if role:
            params["role"] = role
        if search:
            params["search"] = search
        return self._request("GET", "user", "/users", params=params)

    def update_user(self, user_id: str, data: dict):
        return self._request("PUT", "user", f"/users/{user_id}", json=data)

    def get_user_history(self, user_id: str):
        return self._request("GET", "user", f"/users/{user_id}/history")

    # --- Book Service ---
    def get_books(self, search: str = None, category: str = None, available_only: bool = False, include_inactive: bool = False):
        params = {
            "search": search or "",
            "category": category or "",
            "available_only": available_only,
            "include_inactive": include_inactive
        }
        return self._request("GET", "book", "/books", params=params)

    def get_book(self, book_id: int):
        return self._request("GET", "book", f"/books/{book_id}")

    def add_book(self, data: dict):
        return self._request("POST", "book", "/books", json=data)

    def update_book(self, book_id: int, data: dict):
        return self._request("PUT", "book", f"/books/{book_id}", json=data)

    def delete_book(self, book_id: int):
        return self._request("DELETE", "book", f"/books/{book_id}")

    # --- Issue Service ---
    def issue_book(self, user_id: str, book_id: int, issued_by: str = "ADMIN001"):
        return self._request("POST", "issue", "/issues/issue-book", json={
            "user_id": user_id,
            "book_id": book_id,
            "issued_by": issued_by
        })

    def return_book(self, issue_id: int, return_date: str = None):
        payload = {"issue_id": issue_id}
        if return_date:
            payload["return_date"] = return_date
        return self._request("POST", "issue", "/issues/return-book", json=payload)

    def get_issues(self, status: str = None, user_id: str = None):
        params = {}
        if status:
            params["status"] = status
        if user_id:
            params["user_id"] = user_id
        return self._request("GET", "issue", "/issues", params=params)

    def get_issue(self, issue_id: int):
        return self._request("GET", "issue", f"/issues/{issue_id}")

    def get_member_issues(self, user_id: str):
        return self._request("GET", "issue", f"/issues/member/{user_id}")

    def get_overdue_issues(self):
        return self._request("GET", "issue", "/issues/overdue")

    # --- Payment Service ---
    def get_member_fines(self, user_id: str):
        return self._request("GET", "payment", f"/payments/fines/{user_id}")

    def pay_fine(self, fine_id: int, user_id: str, amount: float, payment_method: str = "UPI"):
        return self._request("POST", "payment", "/payments/pay", json={
            "fine_id": fine_id,
            "user_id": user_id,
            "amount": amount,
            "payment_method": payment_method
        })

    def get_payment_history(self, user_id: str):
        return self._request("GET", "payment", f"/payments/history/{user_id}")

    def get_all_payments(self):
        return self._request("GET", "payment", "/payments/all")

    def get_payment_summary(self):
        return self._request("GET", "payment", "/payments/summary")

    # --- Admin Service ---
    def get_admin_dashboard(self):
        return self._request("GET", "admin", "/admin/dashboard")

    def get_admin_members(self):
        return self._request("GET", "admin", "/admin/members")

    def get_admin_books(self):
        return self._request("GET", "admin", "/admin/books")

    def get_issue_reports(self):
        return self._request("GET", "admin", "/admin/reports/issues")

    def get_payment_reports(self):
        return self._request("GET", "admin", "/admin/reports/payments")

    def get_overdue_reports(self):
        return self._request("GET", "admin", "/admin/reports/overdue")

api_client = APIClient()

