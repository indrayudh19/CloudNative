from datetime import datetime, date, timedelta
from database.connection import SessionLocal
from database.models import User, Book, Issue, Fine, Payment, AuditLog
from config import ADMIN_ID, FINE_PER_DAY

def seed():
    db = SessionLocal()
    try:
        # 1. Seed Admin
        admin = db.query(User).filter(User.user_id == ADMIN_ID).first()
        if not admin:
            admin = User(
                user_id=ADMIN_ID,
                name="Library Administrator",
                email="admin@library.org",
                phone="9876543210",
                address="Admin Block, Central Library",
                role="admin",
                status="active",
                created_at=datetime.utcnow() - timedelta(days=60)
            )
            db.add(admin)
            db.commit()
            print("Admin seeded.")

        # 2. Seed Members
        sample_members = [
            ("MEM0001", "Aarav Sharma", "aarav@example.com", "9876543211", "12 Park Street, Delhi"),
            ("MEM0002", "Priya Nair", "priya@example.com", "9876543212", "45 MG Road, Bengaluru"),
            ("MEM0003", "Rohan Mehta", "rohan@example.com", "9876543213", "88 Marine Drive, Mumbai"),
            ("MEM0004", "Ananya Iyer", "ananya@example.com", "9876543214", "23 Anna Salai, Chennai"),
            ("MEM0005", "Arjun Patel", "arjun@example.com", "9876543215", "67 SG Highway, Ahmedabad"),
            ("MEM0006", "Sneha Das", "sneha@example.com", "9876543216", "9 Salt Lake, Kolkata"),
            ("MEM0007", "Karthik Rao", "karthik@example.com", "9876543217", "14 Banjara Hills, Hyderabad"),
            ("MEM0008", "Ishita Gupta", "ishita@example.com", "9876543218", "52 Civil Lines, Jaipur"),
            ("MEM0009", "Aditya Verma", "aditya@example.com", "9876543219", "31 Hazratganj, Lucknow"),
            ("MEM0010", "Meera Krishnan", "meera@example.com", "9876543220", "77 Kaloor, Kochi"),
        ]

        for uid, name, email, phone, addr in sample_members:
            if not db.query(User).filter(User.user_id == uid).first():
                user = User(
                    user_id=uid,
                    name=name,
                    email=email,
                    phone=phone,
                    address=addr,
                    role="member",
                    status="active",
                    created_at=datetime.utcnow() - timedelta(days=30)
                )
                db.add(user)
        db.commit()
        print("Sample members seeded.")

        # 3. Seed Books
        sample_books = [
            ("9780132350884", "Clean Code", "Robert C. Martin", "Programming", "Prentice Hall", 2008, 5),
            ("9780134685991", "Effective Java", "Joshua Bloch", "Programming", "Addison-Wesley", 2017, 4),
            ("9780596007126", "Head First Design Patterns", "Eric Freeman", "Programming", "O'Reilly", 2004, 3),
            ("9780131103627", "The C Programming Language", "Brian Kernighan", "Programming", "Prentice Hall", 1978, 4),
            ("9780262033848", "Introduction to Algorithms", "Thomas H. Cormen", "Computer Science", "MIT Press", 2009, 5),
            ("9781491950296", "Designing Data-Intensive Applications", "Martin Kleppmann", "Technology", "O'Reilly", 2017, 3),
            ("9780135957059", "The Pragmatic Programmer", "David Thomas", "Programming", "Addison-Wesley", 2019, 4),
            ("9780134093413", "Artificial Intelligence: A Modern Approach", "Stuart Russell", "AI", "Pearson", 2020, 3),
            ("9780262046305", "Deep Learning", "Ian Goodfellow", "AI", "MIT Press", 2016, 2),
            ("9780321125217", "Domain-Driven Design", "Eric Evans", "Software Engineering", "Addison-Wesley", 2003, 3),
            ("9780134494166", "Software Engineering", "Ian Sommerville", "Software Engineering", "Pearson", 2015, 4),
            ("9780062315007", "Sapiens", "Yuval Noah Harari", "History", "Harper", 2014, 3),
            ("9780743273565", "The Great Gatsby", "F. Scott Fitzgerald", "Fiction", "Scribner", 1925, 2),
            ("9780451524935", "1984", "George Orwell", "Fiction", "Signet Classic", 1949, 4),
            ("9780141439518", "Pride and Prejudice", "Jane Austen", "Fiction", "Penguin Classics", 1813, 3),
        ]

        for isbn, title, author, cat, pub, yr, copies in sample_books:
            existing_book = db.query(Book).filter(Book.isbn == isbn).first()
            if not existing_book:
                b = Book(
                    isbn=isbn,
                    title=title,
                    author=author,
                    category=cat,
                    publisher=pub,
                    publication_year=yr,
                    total_copies=copies,
                    available_copies=copies,
                    status="active"
                )
                db.add(b)
        db.commit()
        print("Sample books seeded.")

        # 4. Seed Transactions (Idempotent check)
        existing_issues = db.query(Issue).count()
        if existing_issues == 0:
            today = date.today()

            def get_b(title):
                return db.query(Book).filter(Book.title == title).first()

            # MEM0001: Clean Code (Issued recently)
            b1 = get_b("Clean Code")
            iss1 = Issue(
                user_id="MEM0001",
                book_id=b1.book_id,
                issued_by=ADMIN_ID,
                issue_date=today - timedelta(days=5),
                due_date=today + timedelta(days=9),
                status="issued"
            )
            b1.available_copies -= 1
            db.add(iss1)

            # MEM0002: Sapiens (Issued, OVERDUE by 4 days)
            b2 = get_b("Sapiens")
            iss2 = Issue(
                user_id="MEM0002",
                book_id=b2.book_id,
                issued_by=ADMIN_ID,
                issue_date=today - timedelta(days=18),
                due_date=today - timedelta(days=4),
                status="issued"
            )
            b2.available_copies -= 1
            db.add(iss2)
            db.flush()

            # Fine for MEM0002 overdue
            fine2 = Fine(
                issue_id=iss2.issue_id,
                user_id="MEM0002",
                amount=20.0,
                paid_amount=0.0,
                outstanding_amount=20.0,
                status="unpaid",
                created_at=datetime.utcnow() - timedelta(days=1)
            )
            db.add(fine2)

            # MEM0003: Introduction to Algorithms (Issued recently)
            b3 = get_b("Introduction to Algorithms")
            iss3 = Issue(
                user_id="MEM0003",
                book_id=b3.book_id,
                issued_by=ADMIN_ID,
                issue_date=today - timedelta(days=2),
                due_date=today + timedelta(days=12),
                status="issued"
            )
            b3.available_copies -= 1
            db.add(iss3)

            # MEM0004: Deep Learning (Issued recently)
            b4 = get_b("Deep Learning")
            iss4 = Issue(
                user_id="MEM0004",
                book_id=b4.book_id,
                issued_by=ADMIN_ID,
                issue_date=today - timedelta(days=7),
                due_date=today + timedelta(days=7),
                status="issued"
            )
            b4.available_copies -= 1
            db.add(iss4)

            # MEM0005: 1984 (Returned late, fine paid!)
            b5 = get_b("1984")
            iss5 = Issue(
                user_id="MEM0005",
                book_id=b5.book_id,
                issued_by=ADMIN_ID,
                issue_date=today - timedelta(days=25),
                due_date=today - timedelta(days=11),
                return_date=today - timedelta(days=8),
                status="returned"
            )
            db.add(iss5)
            db.flush()

            fine5 = Fine(
                issue_id=iss5.issue_id,
                user_id="MEM0005",
                amount=15.0,
                paid_amount=15.0,
                outstanding_amount=0.0,
                status="paid",
                created_at=datetime.utcnow() - timedelta(days=8)
            )
            db.add(fine5)
            db.flush()

            pay5 = Payment(
                fine_id=fine5.fine_id,
                user_id="MEM0005",
                amount=15.0,
                payment_date=datetime.utcnow() - timedelta(days=7),
                payment_method="UPI",
                status="successful",
                transaction_reference="TXN-MEM0005-INIT01"
            )
            db.add(pay5)

            # Audit log entry for initial seed
            log = AuditLog(
                user_id=ADMIN_ID,
                action="Database Seed Initialization",
                entity_type="System",
                entity_id="ALL",
                timestamp=datetime.utcnow()
            )
            db.add(log)

            db.commit()
            print("Demonstration transactions, fines, and payments seeded.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()

