import subprocess
import sys
import time
import os

SERVICES = [
    ("User Service", "services.userservice.main:app", 8001),
    ("Book Service", "services.bookservice.main:app", 8002),
    ("Issue Service", "services.issueservice.main:app", 8003),
    ("Payment Service", "services.paymentservice.main:app", 8004),
    ("Admin Service", "services.adminservice.main:app", 8005),
]

def main():
    print("=" * 60)
    print("Starting LMS Microservices & Streamlit Application")
    print("=" * 60)

    # Initialize and seed database if not already done
    if not os.path.exists("database/lms.db"):
        print("Database not found. Initializing and seeding...")
        subprocess.run([sys.executable, "-m", "database.init_db"], check=True)
        subprocess.run([sys.executable, "-m", "database.seed_data"], check=True)

    processes = []
    try:
        # Start backend services
        for name, app_str, port in SERVICES:
            print(f"Starting {name} on port {port}...")
            p = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", app_str, "--host", "127.0.0.1", "--port", str(port)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            processes.append((name, p))
            time.sleep(0.5)

        print("\nAll 5 backend services started successfully.")
        print("API Documentation:")
        for name, _, port in SERVICES:
            print(f"  - {name}: http://localhost:{port}/docs")

        print("\nLaunching Streamlit frontend on http://localhost:8501 ...")
        st_proc = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"]
        )
        processes.append(("Streamlit App", st_proc))

        print("\nPress Ctrl+C to stop all services.")
        st_proc.wait()

    except KeyboardInterrupt:
        print("\nStopping all services...")
    finally:
        for name, p in processes:
            print(f"Terminating {name}...")
            p.terminate()
            p.wait()
        print("All processes stopped.")

if __name__ == "__main__":
    main()


