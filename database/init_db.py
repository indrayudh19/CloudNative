import os
from database.connection import engine, Base
import database.models  # Ensure models are loaded

def init_database():
    os.makedirs("database", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_database()

