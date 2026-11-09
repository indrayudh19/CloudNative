from fastapi.testclient import TestClient
from services.userservice.main import app as user_app
from services.bookservice.main import app as book_app
from services.issueservice.main import app as issue_app
from services.paymentservice.main import app as pay_app
from services.adminservice.main import app as admin_app

c_user = TestClient(user_app)
c_book = TestClient(book_app)
c_issue = TestClient(issue_app)
c_pay = TestClient(pay_app)
c_admin = TestClient(admin_app)

def test_full_flow():
    # 1. Test User Login
    r1 = c_user.post("/users/login", json={"user_id": "ADMIN001"})
    assert r1.status_code == 200 and r1.json()["role"] == "admin", f"User login failed: {r1.text}"
    print("✓ User Service: Admin login test passed")

    # 2. Test User Registration with Auto-generated ID
    r2 = c_user.post("/users/register", json={"name": "Test Student", "email": "student_test_run@example.com", "phone": "9876543299"})
    if r2.status_code != 200 and "already registered" in r2.text:
        # fetch existing user
        users = c_user.get("/users?search=student_test_run").json()
        new_uid = users[0]["user_id"]
    else:
        assert r2.status_code == 200, f"User registration failed: {r2.text}"
        new_uid = r2.json()["user_id"]
    
    assert new_uid.startswith("MEM"), f"Invalid member id format: {new_uid}"
    print(f"✓ User Service: Auto ID generation verified: {new_uid}")

    # 3. Test Book Service List
    r3 = c_book.get("/books")
    assert r3.status_code == 200 and len(r3.json()) >= 15, f"Book listing failed: {r3.text}"
    print(f"✓ Book Service: Listed {len(r3.json())} books")

    # 4. Test Issue Service: Issue book to member
    available_books = [b for b in r3.json() if b["available_copies"] > 0]
    first_book = available_books[0]
    b_id = first_book["book_id"]
    r4 = c_issue.post("/issues/issue-book", json={"user_id": new_uid, "book_id": b_id})
    assert r4.status_code == 200, f"Issue book failed: {r4.text}"
    issue_id = r4.json()["issue_id"]
    print(f"✓ Issue Service: Issued book ID {b_id} to {new_uid}, issue_id: {issue_id}")

    # 5. Return book
    r5 = c_issue.post("/issues/return-book", json={"issue_id": issue_id})
    assert r5.status_code == 200, f"Return book failed: {r5.text}"
    print(f"✓ Issue Service: Returned book issue #{issue_id}")

    # 6. Test Admin Dashboard
    r6 = c_admin.get("/admin/dashboard")
    assert r6.status_code == 200 and "total_registered_members" in r6.json(), f"Admin dashboard failed: {r6.text}"
    print(f"✓ Admin Service: Dashboard metrics retrieved successfully (Total members: {r6.json()['total_registered_members']})")

    # 7. Test Payment Summary
    r7 = c_pay.get("/payments/summary")
    assert r7.status_code == 200 and "total_collected" in r7.json(), f"Payment summary failed: {r7.text}"
    print(f"✓ Payment Service: Summary retrieved successfully: {r7.json()}")

    print("\n==============================================")
    print("ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("==============================================")

if __name__ == "__main__":
    test_full_flow()

