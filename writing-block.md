# Library Management System (LMS)
## Build Specification and Technical Architecture

**Technology Stack:** Python, Streamlit, SQLite, FastAPI (service communication), SQLAlchemy

---

# 1. Project Overview

Develop a Library Management System (LMS) using Python and Streamlit with a modular microservice-based architecture.

The system will support two types of users:

1. Member
2. Admin

Members can browse the library catalog, view their borrowing history, check their outstanding fines, and make fine payments.

Administrators will have complete control over library operations, including book management, member management, issuing and returning books, fine management, and monitoring library activity.

The application should have a clean, modern dashboard interface with separate experiences for members and administrators.

## 1.1 Core Objectives

- Implement role-based access control.
- Separate business functionality into independent services.
- Maintain a relational database with interconnected tables.
- Automatically generate member IDs.
- Track every book issue and return.
- Automatically calculate overdue fines.
- Reflect database changes throughout the application.
- Provide an intuitive Streamlit interface.

# 2. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Frontend | Streamlit |
| Database | SQLite |
| Database ORM | SQLAlchemy |
| Backend services | FastAPI |
| API communication | REST APIs |
| Data validation | Pydantic |
| Charts and reports | Plotly |
| Date handling | Python datetime |

### Why SQLite?

SQLite will be used instead of MySQL.

- No separate database server is needed.
- No MySQL Workbench installation is required.
- The database is stored locally as `lms.db`.
- Python can directly interact with it.
- It supports relational tables and foreign-key constraints.
- It is sufficient for this project and local demonstration.

All services will initially use the same SQLite database file. Each service will own its business logic and database operations through its respective repository.

This is a lightweight local microservice-style deployment. The services should communicate through defined interfaces, preferably REST APIs. The shared database is a deliberate simplification for the initial version; independently deployed production microservices would normally own separate databases.

# 3. Project Directory Structure

Create the following directory structure:

```text
LMS/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── build.md
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── models.py
│   ├── init_db.py
│   └── seed_data.py
│
├── services/
│   │
│   ├── userservice/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── user_logic.py
│   │   └── repository.py
│   │
│   ├── bookservice/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── book_logic.py
│   │   └── repository.py
│   │
│   ├── issueservice/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── issue_logic.py
│   │   └── repository.py
│   │
│   ├── paymentservice/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── payment_logic.py
│   │   └── repository.py
│   │
│   └── adminservice/
│       ├── __init__.py
│       ├── main.py
│       ├── routes.py
│       ├── admin_logic.py
│       └── repository.py
│
├── frontend/
│   ├── __init__.py
│   ├── login.py
│   ├── member_dashboard.py
│   ├── admin_dashboard.py
│   ├── components.py
│   └── styles.py
│
├── utils/
│   ├── __init__.py
│   ├── auth.py
│   ├── api_client.py
│   └── helpers.py
│
└── assets/
    └── logo.png
```

# 4. User Roles and Permissions

There will be two roles in the application.

## 4.1 Member

A member can perform the following operations:

### A. Dashboard

Display:
- Total books currently borrowed by the member.
- Outstanding fine amount.
- Total borrowing transactions.
- Recently borrowed books.
- Books currently overdue.

### B. Browse Book Catalog

Display the complete book catalog.

Each book should display:

- Book title
- Author
- ISBN
- Category
- Publication year
- Availability status
- Available copies

Include:
- Search by book title.
- Search by author.
- Filter by category.
- Filter by availability.

Members can only view the catalog. They cannot directly issue or return books.

### C. Issue History

Display the member's complete borrowing history.

The history should include:

| Field | Description |
|---|---|
| Issue ID | Unique transaction ID |
| Book Name | Name of the borrowed book |
| Author | Book author |
| Date of Issue | Date the book was issued |
| Due Date | Expected return date |
| Date of Return | Actual return date, if returned |
| Status | Issued / Returned / Overdue |
| Fine | Fine generated for the transaction |

Allow filtering by:
- Currently issued books.
- Returned books.
- Overdue books.
- All transactions.

### D. Fine and Payment Section

Members should be able to:
- View outstanding fines.
- View the reason for each fine.
- View fine amount.
- View payment history.
- Pay outstanding fines.

Payment will be simulated for the local project. No real payment gateway or banking integration is required.

Once payment is successful:
- Update the payment record.
- Update the fine's paid amount.
- Recalculate its outstanding balance.
- Mark the fine as paid if its balance reaches zero.
- Reflect the updated amount immediately in the member dashboard.

Members must only access their own transactions and fines.

## 4.2 Admin

Admin has complete access to the application.

### A. Admin Dashboard

Display the following statistics:

- Total registered members.
- Total books in the library.
- Total available copies.
- Total currently issued books.
- Total overdue books.
- Total outstanding fines.
- Total fines collected.

Include charts for:
- Books issued over time.
- Most borrowed books.
- Fine collection.
- Member activity.

### B. Member Management

Admin can:
- View all registered members.
- Search members by ID or name.
- View member details.
- View borrowing history of any member.
- View outstanding fines.
- View membership status.
- Activate or deactivate members.

Admin should not be able to accidentally delete members with existing transaction history. Prefer deactivation instead.

### C. Book Management

Admin can:
- Add a new book.
- Edit book details.
- Remove a book from circulation.
- Update the number of available copies.
- View total copies.
- View issued copies.
- Search and filter books.

Book details:

- Title
- Author
- ISBN
- Category
- Publisher
- Publication year
- Total copies
- Available copies

Prevent deletion of books with active borrowing transactions. Use an inactive/archived status instead.

### D. Issue a Book

Admin can issue a book to a registered member.

Workflow:

1. Search for the member using their Member ID.
2. Display member details.
3. Search for the requested book.
4. Check book availability.
5. Verify that the member is active.
6. Verify that the member has not exceeded the borrowing limit.
7. Verify that the member has no borrowing restriction due to unpaid fines.
8. Confirm the transaction.
9. Create an issue record.
10. Decrease the available book count by one.

Default borrowing rules:

- Maximum active issues per member: 3.
- Borrowing period: 14 days.
- Issue date: Current date.
- Due date: Issue date + 14 days.

These values should be configurable in `config.py`.

### E. Return a Book

Admin can return a previously issued book.

Workflow:

1. Search by Issue ID, Member ID, or Book Name.
2. Display the borrowing transaction.
3. Calculate whether the book is overdue.
4. Calculate the fine if applicable.
5. Confirm return.
6. Update the issue status to Returned.
7. Store the actual return date.
8. Increase the book's available copies by one.
9. Create a fine record if an overdue fine applies.

Default fine policy:

- Fine per overdue day: ₹5.
- Fine = Number of overdue days × ₹5.
- No fine if returned on or before the due date.

The fine amount should be configurable.

### F. Fine Management

Admin can:
- View all fines.
- Search fines by member.
- View paid and unpaid fines.
- View partial payments.
- View total fine collection.
- View outstanding amounts.

### G. Transaction Monitoring

Admin should have access to:
- All issue transactions.
- All return transactions.
- All payment transactions.
- Member-specific borrowing activity.
- Book-specific borrowing activity.

# 5. Login and Registration System

## 5.1 Login Page

The initial page should contain:

- Application name and logo.
- User ID input.
- Password input.
- Login button.
- New User registration option.

Authentication is intentionally simplified for this project.

**Login rules:**

1. User enters an ID.
2. The system checks whether the ID exists.
3. If the ID exists and is active, allow login.
4. Password is accepted without verification.
5. Identify the user's role.
6. Redirect to the corresponding dashboard.

If the ID does not exist, show:

"Invalid User ID. Please check your ID or register as a new member."

There will be no password verification in this demonstration version. This is strictly a dummy authentication mechanism and must not be used in a real deployed application.

## 5.2 Admin Login

Admin ID:

`ADMIN001`

Admin password:

Any non-empty value.

Admin should be seeded into the database during initialization.

Admin registration through the New User option must not be allowed.

## 5.3 New User Registration

The login page should include a New User option.

On clicking it, open a registration form with:

- Full name
- Email
- Phone number
- Address
- Date of birth (optional)

On submission:

1. Validate the required fields.
2. Check that the email is not already registered.
3. Generate a unique Member ID automatically.
4. Insert the new member into the database.
5. Assign the role `member`.
6. Set membership status to `active`.
7. Display the generated Member ID.

Example Member IDs:

```text
MEM0001
MEM0002
MEM0003
MEM0004
```

The generated ID should be shown prominently:

"Registration successful! Your Member ID is MEM0011. Use this ID to log in."

The member must use this generated ID for subsequent logins.

# 6. Database Architecture

Use SQLite with SQLAlchemy.

Database filename:

`database/lms.db`

All tables should be connected through primary keys and foreign keys.

## 6.1 Database Tables

Create the following tables.

### Table 1: users

Stores members and administrators.

| Column | Type | Description |
|---|---|---|
| user_id | TEXT | Primary key |
| name | TEXT | Full name |
| email | TEXT | Unique email |
| phone | TEXT | Phone number |
| address | TEXT | Address |
| role | TEXT | member / admin |
| status | TEXT | active / inactive |
| created_at | DATETIME | Registration date |

Admin ID will be `ADMIN001`.

Member IDs will be automatically generated.

### Table 2: books

Stores the library catalog.

| Column | Type | Description |
|---|---|---|
| book_id | INTEGER | Primary key |
| isbn | TEXT | Unique ISBN |
| title | TEXT | Book title |
| author | TEXT | Author |
| category | TEXT | Category |
| publisher | TEXT | Publisher |
| publication_year | INTEGER | Year |
| total_copies | INTEGER | Total copies |
| available_copies | INTEGER | Available copies |
| status | TEXT | active / inactive |

### Table 3: issues

Stores all borrowing transactions.

| Column | Type | Description |
|---|---|---|
| issue_id | INTEGER | Primary key |
| user_id | TEXT | FK → users.user_id |
| book_id | INTEGER | FK → books.book_id |
| issued_by | TEXT | FK → users.user_id |
| issue_date | DATE | Issue date |
| due_date | DATE | Due date |
| return_date | DATE | Actual return date |
| status | TEXT | issued / returned |
 
This table connects users and books.

A book can have many borrowing records, and a member can borrow many books.

### Table 4: fines

Stores fine information.

| Column | Type | Description |
|---|---|---|
| fine_id | INTEGER | Primary key |
| issue_id | INTEGER | FK → issues.issue_id |
| user_id | TEXT | FK → users.user_id |
| amount | DECIMAL | Original fine amount |
| paid_amount | DECIMAL | Amount already paid |
| outstanding_amount | DECIMAL | Remaining balance |
| status | TEXT | unpaid / partial / paid |
| created_at | DATETIME | Fine creation date |

Each fine belongs to a particular issue transaction and member.

### Table 5: payments

Stores payment history.

| Column | Type | Description |
|---|---|---|
| payment_id | INTEGER | Primary key |
| fine_id | INTEGER | FK → fines.fine_id |
| user_id | TEXT | FK → users.user_id |
| amount | DECIMAL | Amount paid |
| payment_date | DATETIME | Payment timestamp |
| payment_method | TEXT | Cash / UPI / Card (simulated) |
| status | TEXT | successful / failed |
| transaction_reference | TEXT | Unique transaction reference |

One fine can have multiple payment records, allowing partial payments.

### Table 6: audit_logs

Tracks important administrative activities.

| Column | Type | Description |
|---|---|---|
| log_id | INTEGER | Primary key |
| user_id | TEXT | FK → users.user_id |
| action | TEXT | Action performed |
| entity_type | TEXT | Book / User / Issue / Payment |
| entity_id | TEXT | Related record ID |
| timestamp | DATETIME | Action timestamp |

This table will help monitor administrative operations.

## 6.2 Database Relationships

The relational structure should follow:

```text
USERS
  |
  | 1:N
  |
  +---------- ISSUES ---------- BOOKS
  |                |               |
  |                | 1:1 or 1:0..1 |
  |                |               |
  |              FINES             |
  |                |               |
  |                | 1:N           |
  |                |               |
  |             PAYMENTS           |
  |
  +---------- AUDIT_LOGS
```

More precisely:

- One user can have multiple issue records.
- One book can appear in multiple issue records.
- Each issue belongs to one member and one book.
- An issue can have zero or one fine record.
- Each fine can have multiple payment records.
- One user can have multiple payment records.
- One administrator can perform multiple issue operations.
- One user can have multiple audit log entries.

Enable SQLite foreign-key enforcement using:

`PRAGMA foreign_keys = ON;`

Use SQLAlchemy relationships where appropriate.

## 6.3 Database Consistency Requirements

The following rules are essential:

1. Available copies must never be negative.
2. Available copies must never exceed total copies.
3. An issue cannot be created when a book has zero available copies.
4. A member cannot exceed the borrowing limit.
5. A returned book cannot be returned again.
6. Returning a book must update the corresponding book inventory.
7. A payment cannot exceed the outstanding fine balance.
8. Every payment must have a corresponding fine and member.
9. The paid amount must never exceed the original fine.
10. All related changes must occur within database transactions.

For example, issuing a book must atomically create the issue record and decrease available copies. If either operation fails, both must be rolled back.

# 7. Initial Database Seed Data

The database should be populated automatically when initialized.

Do not require manual database entry.

## 7.1 Initial Admin

| User ID | Name | Role |
|---|---|---|
| ADMIN001 | Library Administrator | admin |

## 7.2 Initial Members

Insert 10 sample members.

| User ID | Name | Email |
|---|---|---|
| MEM0001 | Aarav Sharma | aarav@example.com |
| MEM0002 | Priya Nair | priya@example.com |
| MEM0003 | Rohan Mehta | rohan@example.com |
| MEM0004 | Ananya Iyer | ananya@example.com |
| MEM0005 | Arjun Patel | arjun@example.com |
| MEM0006 | Sneha Das | sneha@example.com |
| MEM0007 | Karthik Rao | karthik@example.com |
| MEM0008 | Ishita Gupta | ishita@example.com |
| MEM0009 | Aditya Verma | aditya@example.com |
| MEM0010 | Meera Krishnan | meera@example.com |

All sample members should have active membership status.

Include realistic phone numbers, addresses, and registration dates as sample data.

## 7.3 Initial Books

Insert at least 15 books.

| ISBN | Title | Author | Category | Total Copies |
|---|---|---|---|---|
| 9780132350884 | Clean Code | Robert C. Martin | Programming | 5 |
| 9780134685991 | Effective Java | Joshua Bloch | Programming | 4 |
| 9780596007126 | Head First Design Patterns | Eric Freeman | Programming | 3 |
| 9780131103627 | The C Programming Language | Brian Kernighan | Programming | 4 |
| 9780262033848 | Introduction to Algorithms | Thomas H. Cormen | Computer Science | 5 |
| 9781491950296 | Designing Data-Intensive Applications | Martin Kleppmann | Technology | 3 |
| 9780135957059 | The Pragmatic Programmer | David Thomas | Programming | 4 |
| 9780134093413 | Artificial Intelligence: A Modern Approach | Stuart Russell | AI | 3 |
| 9780262046305 | Deep Learning | Ian Goodfellow | AI | 2 |
| 9780321125217 | Domain-Driven Design | Eric Evans | Software Engineering | 3 |
| 9780134494166 | Software Engineering | Ian Sommerville | Software Engineering | 4 |
| 9780062315007 | Sapiens | Yuval Noah Harari | History | 3 |
| 9780743273565 | The Great Gatsby | F. Scott Fitzgerald | Fiction | 2 |
| 9780451524935 | 1984 | George Orwell | Fiction | 4 |
| 9780141439518 | Pride and Prejudice | Jane Austen | Fiction | 3 |

Available copies should initially equal total copies.

ISBN values should be stored as strings, not integers.

## 7.4 Sample Transaction Data

Also create a few initial issue records for demonstration purposes.

For example:

- MEM0001 has borrowed Clean Code.
- MEM0002 has borrowed Sapiens.
- MEM0003 has borrowed Introduction to Algorithms.
- MEM0004 has borrowed Deep Learning.
- MEM0005 has returned 1984.

Include at least one overdue issue with an outstanding fine and one paid fine so that the payment dashboard can be demonstrated immediately.

Make sure the sample issue records and available book counts remain consistent.

Seed scripts must be idempotent: running initialization again must not duplicate sample users, books, or transactions.

# 8. Microservice Responsibilities

Each service should own its business logic and expose clear interfaces.

## 8.1 User Service

Responsibilities:

- Member registration.
- ID generation.
- Login validation.
- Role identification.
- Member information.
- Member status management.
- Member search.

Suggested API endpoints:

```text
POST /users/register
POST /users/login
GET  /users/{user_id}
GET  /users
PUT  /users/{user_id}
GET  /users/{user_id}/history
```

## 8.2 Book Service

Responsibilities:

- Add books.
- Update books.
- Search books.
- Retrieve catalog.
- Update inventory.
- Archive books.
- Check book availability.

Suggested endpoints:

```text
GET    /books
GET    /books/{book_id}
POST   /books
PUT    /books/{book_id}
DELETE /books/{book_id}
GET    /books/search
```

Use soft deletion for books with existing transaction history.

## 8.3 Issue Service

Responsibilities:

- Issue books.
- Return books.
- Check borrowing eligibility.
- Maintain issue history.
- Calculate overdue days.
- Trigger fine creation.

Suggested endpoints:

```text
POST /issues/issue-book
POST /issues/return-book
GET  /issues
GET  /issues/{issue_id}
GET  /issues/member/{user_id}
GET  /issues/overdue
```

This service should coordinate with the Book Service and Payment/Fine functionality through defined service interfaces.

## 8.4 Payment Service

Responsibilities:

- Retrieve member fines.
- Calculate outstanding balances.
- Process simulated payments.
- Generate transaction references.
- Maintain payment history.
- Update fine status.

Suggested endpoints:

```text
GET  /payments/fines/{user_id}
POST /payments/pay
GET  /payments/history/{user_id}
GET  /payments/all
GET  /payments/summary
```

Simulated payment should validate the requested amount and update the payment and fine records atomically.

## 8.5 Admin Service

Responsibilities:

- Retrieve library-wide statistics.
- Monitor members.
- Monitor book inventory.
- Retrieve transaction reports.
- Retrieve overdue reports.
- Retrieve payment reports.
- Record administrative actions.

Suggested endpoints:

```text
GET /admin/dashboard
GET /admin/members
GET /admin/books
GET /admin/reports/issues
GET /admin/reports/payments
GET /admin/reports/overdue
```

The Admin Service should primarily aggregate information from the other services instead of duplicating their business logic.

# 9. Frontend Design

Use Streamlit with a clean sidebar-based navigation system.

## 9.1 Login Page

Design:

- Application logo and title.
- User ID field.
- Password field.
- Login button.
- New User button.

The login page should be the initial entry point.

## 9.2 Member Dashboard

Sidebar:

```text
Library Management System

Welcome, Member

- Dashboard
- Browse Catalog
- My Issue History
- My Fines & Payments
- My Profile

- Logout
```

Dashboard layout:

First row:
- Books Currently Borrowed
- Outstanding Fine
- Total Issues

Second row:
- Recently Borrowed Books
- Overdue Notifications

Use Streamlit metrics, tables, and Plotly charts where useful.

## 9.3 Admin Dashboard

Sidebar:

```text
Library Management System

Administrator

- Dashboard
- Manage Books
- Manage Members
- Issue Book
- Return Book
- Fine Management
- Transaction History
- Reports

- Logout
```

The admin dashboard should have an analytics-oriented layout.

Use:
- Metric cards.
- Data tables.
- Search and filtering.
- Charts.
- Confirmation dialogs for important operations.

# 10. Application Workflows

## Workflow A: New Member Registration

```text
Login Page
    |
New User
    |
Registration Form
    |
Validate Information
    |
Generate Member ID
    |
Insert into Users Table
    |
Registration Successful
    |
Display Member ID
```

## Workflow B: Member Login

```text
Login Page
    |
Enter User ID and Password
    |
Check User ID
    |
Validate Membership Status
    |
Identify Role
    |
Member Dashboard
```

Admin login follows the same flow, with the role redirecting to Admin Dashboard.

## Workflow C: Issue a Book

```text
Admin Dashboard
    |
Issue Book
    |
Select Member
    |
Select Book
    |
Check Eligibility
    |
Check Availability
    |
Confirm Issue
    |
Create Issue Record
    |
Decrease Available Copies
    |
Success Notification
```

## Workflow D: Return a Book

```text
Admin Dashboard
    |
Return Book
    |
Find Issue Record
    |
Calculate Overdue Days
    |
Calculate Fine
    |
Confirm Return
    |
Update Issue Status
    |
Update Book Inventory
    |
Create Fine If Required
    |
Success Notification
```

## Workflow E: Pay Fine

```text
Member Dashboard
    |
My Fines & Payments
    |
Select Outstanding Fine
    |
Enter Payment Amount
    |
Select Simulated Payment Method
    |
Confirm Payment
    |
Validate Amount
    |
Create Payment Record
    |
Update Fine Balance
    |
Display Receipt
```

# 11. Important Business Rules

Implement the following rules centrally within the services.

1. Only administrators can issue books.
2. Only administrators can process book returns.
3. Members can only view their own borrowing history.
4. Members can only view and pay their own fines.
5. Members cannot access administrative pages or endpoints.
6. Inactive members cannot borrow books.
7. Inactive books cannot be issued.
8. A book must have available inventory before issuance.
9. A member can borrow a maximum of three books simultaneously.
10. The default borrowing period is 14 days.
11. Fine is ₹5 per overdue day.
12. Partial payments are supported.
13. Payment cannot exceed the outstanding fine.
14. All transactions must maintain database consistency.
15. Logging out must clear the current Streamlit session.

Role validation must be performed in backend services, not just by hiding Streamlit navigation options.

# 12. Configuration

Create a `config.py` file.

Centralize configurable values:

```python
ADMIN_ID = "ADMIN001"

MAX_BOOKS_PER_MEMBER = 3

LOAN_PERIOD_DAYS = 14

FINE_PER_DAY = 5.0

DATABASE_URL = "sqlite:///database/lms.db"
```

Avoid hardcoding these values throughout the services.

# 13. Requirements

The initial `requirements.txt` should contain:

```text
streamlit
fastapi
uvicorn
sqlalchemy
pydantic
requests
pandas
plotly
```

SQLite support is already included in standard Python installations.

# 14. Running the Application

The application should be executable locally on Windows.

Initial setup:

```powershell
python -m venv venv

.\venv\Scripts\activate

pip install -r requirements.txt
```

Initialize the database:

```powershell
python -m database.init_db
```

Start the backend services on separate local ports:

```text
User Service      : 8001
Book Service      : 8002
Issue Service     : 8003
Payment Service   : 8004
Admin Service     : 8005
```

Each FastAPI service should expose its own `/docs` endpoint for API testing.

For example:

```text
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
http://localhost:8004/docs
http://localhost:8005/docs
```

Start Streamlit:

```powershell
streamlit run app.py
```

Application URL:

```text
http://localhost:8501
```

Provide a startup script such as `run_all.py` or `start_services.ps1` to start all five services and the Streamlit application conveniently.

# 15. Expected Deliverables

The completed project must include:

1. A working Streamlit login page.
2. Automatic member registration and ID generation.
3. A fixed administrator account.
4. Separate member and administrator dashboards.
5. A working book catalog.
6. Book management functionality.
7. Book issue and return functionality.
8. Complete issue history.
9. Automatic overdue fine calculation.
10. Simulated fine payment.
11. Payment history and receipts.
12. Admin analytics dashboard.
13. Interconnected SQLite database.
14. Five logically separated backend services.
15. REST API documentation through FastAPI Swagger.
16. Sample database with 10 members, 15 books, and demonstration transactions.

# 16. Implementation Guidelines

Follow these guidelines throughout development:

- Keep the frontend separate from backend business logic.
- Do not put SQL queries directly inside Streamlit pages.
- Each service must own its business operations.
- Use SQLAlchemy models and repositories.
- Keep database initialization and seed data separate.
- Use reusable functions and components.
- Implement proper error handling.
- Validate all inputs.
- Use database transactions for operations involving multiple tables.
- Maintain consistent foreign-key relationships.
- Avoid duplicating business logic across services.
- Use Streamlit session state for the current login session.
- Refresh dashboard data after every successful operation.
- Do not use hardcoded sample values in dashboard metrics; retrieve actual values from the database.

**Important:** The dummy password authentication is only for the academic demonstration. If the project is deployed publicly, replace it with password hashing, real authentication, and proper authorization.

# 17. Development Order

Build the application in the following sequence:

**Phase 1 — Database**

- Create SQLite database.
- Create all six relational tables.
- Define primary and foreign keys.
- Insert initial admin, members, books, and demonstration transactions.
- Verify database relationships.

**Phase 2 — Backend Services**

- Implement User Service.
- Implement Book Service.
- Implement Issue Service.
- Implement Payment Service.
- Implement Admin Service.
- Test each API independently.

**Phase 3 — Authentication**

- Build login page.
- Implement dummy password authentication.
- Implement admin and member role detection.
- Implement member registration.
- Implement automatic ID generation.

**Phase 4 — Member Interface**

- Build member dashboard.
- Build catalog.
- Build issue history.
- Build fine and payment pages.

**Phase 5 — Admin Interface**

- Build admin dashboard.
- Build member management.
- Build book management.
- Implement issue and return operations.
- Build fine management and reports.

**Phase 6 — Integration and Testing**

- Test all services together.
- Verify that book inventory updates after issuing and returning.
- Verify that fines are created correctly.
- Verify that payments update outstanding balances.
- Verify that members cannot access admin operations.
- Test invalid IDs, inactive users, unavailable books, and duplicate returns.
- Verify that all changes persist after restarting the application.

---

**Final Expected Result:** A fully functional, locally running Library Management System with separate member and administrator interfaces, five backend services, a relational SQLite database, automated ID generation, complete borrowing workflows, and fine/payment management.