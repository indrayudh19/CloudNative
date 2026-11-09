
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from datetime import datetime

# ==========================================================
# CONFIGURATION
# ==========================================================

SERVICES = {
    "User Service": {
        "url": "http://127.0.0.1:8001",
        "endpoints": ["/users"]
    },
    "Book Service": {
        "url": "http://127.0.0.1:8002",
        "endpoints": ["/books"]
    },
    "Issue Service": {
        "url": "http://127.0.0.1:8003",
        "endpoints": ["/issues"]
    },
    "Payment Service": {
        "url": "http://127.0.0.1:8004",
        "endpoints": ["/payments/all"]
    },
    "Admin Service": {
        "url": "http://127.0.0.1:8005",
        "endpoints": ["/admin/dashboard"]
    }
}

REQUESTS_PER_ENDPOINT = 20
CONCURRENT_USERS = 5
TIMEOUT = 10

# ==========================================================
# REQUEST EXECUTION
# ==========================================================

def send_request(url):

    start = time.perf_counter()

    try:
        response = requests.get(url, timeout=TIMEOUT)

        elapsed = (time.perf_counter() - start) * 1000

        return {
            "status": response.status_code,
            "time": elapsed,
            "success": 200 <= response.status_code < 400,
            "error": None
        }

    except requests.exceptions.RequestException as e:

        elapsed = (time.perf_counter() - start) * 1000

        return {
            "status": None,
            "time": elapsed,
            "success": False,
            "error": str(e)
        }


# ==========================================================
# PERFORMANCE TEST
# ==========================================================

def test_endpoint(service_name, base_url, endpoint):

    url = base_url.rstrip("/") + endpoint

    print(f"\nTesting: {service_name} | {endpoint}")

    # Warm-up request (excluded from metrics)
    warmup = send_request(url)

    if warmup["error"]:
        print("Warning: Warm-up request failed.")

    results = []

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:

        futures = [
            executor.submit(send_request, url)
            for _ in range(REQUESTS_PER_ENDPOINT)
        ]

        for future in as_completed(futures):
            results.append(future.result())

    total_time = time.perf_counter() - start_time

    # Extract metrics
    response_times = [r["time"] for r in results]
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    response_times.sort()

    avg = statistics.mean(response_times)
    minimum = min(response_times)
    maximum = max(response_times)
    median = statistics.median(response_times)

    p95_index = max(0, int(0.95 * len(response_times) + 0.999999) - 1)
    p95 = response_times[p95_index]

    rps = len(results) / total_time if total_time > 0 else 0

    status_counts = Counter(
        str(r["status"]) if r["status"] is not None else "ERROR"
        for r in results
    )

    print("-" * 55)
    print(f"Total Requests      : {len(results)}")
    print(f"Successful Requests : {len(successful)}")
    print(f"Failed Requests     : {len(failed)}")
    print(f"Average Response    : {avg:.2f} ms")
    print(f"Minimum Response    : {minimum:.2f} ms")
    print(f"Maximum Response    : {maximum:.2f} ms")
    print(f"Median Response     : {median:.2f} ms")
    print(f"P95 Response        : {p95:.2f} ms")
    print(f"Requests Per Second : {rps:.2f}")
    print(f"Total Test Duration : {total_time:.2f} seconds")
    print(f"HTTP Status Counts  : {dict(status_counts)}")

    if failed:
        print("\nErrors:")
        for error in failed[:3]:
            print(f"  Status: {error['status']} | {error['error']}")

    return {
        "service": service_name,
        "endpoint": endpoint,
        "requests": len(results),
        "success": len(successful),
        "failed": len(failed),
        "avg": avg,
        "min": minimum,
        "max": maximum,
        "median": median,
        "p95": p95,
        "rps": rps,
        "duration": total_time
    }


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 65)
    print("       LIBRARY MANAGEMENT SYSTEM")
    print("       MICROSERVICE PERFORMANCE TEST")
    print("=" * 65)

    print(f"Test Started : {datetime.now()}")
    print(f"Requests per endpoint : {REQUESTS_PER_ENDPOINT}")
    print(f"Concurrent workers    : {CONCURRENT_USERS}")

    all_results = []

    for service_name, details in SERVICES.items():

        print("\n" + "=" * 65)
        print(f"SERVICE: {service_name}")
        print("=" * 65)

        for endpoint in details["endpoints"]:

            result = test_endpoint(
                service_name,
                details["url"],
                endpoint
            )

            all_results.append(result)

    # ======================================================
    # FINAL SUMMARY
    # ======================================================

    print("\n\n")
    print("=" * 90)
    print("                 FINAL PERFORMANCE SUMMARY")
    print("=" * 90)

    print(
        f"{'SERVICE':<18}"
        f"{'AVG (ms)':<13}"
        f"{'P95 (ms)':<13}"
        f"{'SUCCESS':<12}"
        f"{'FAILED':<10}"
        f"{'RPS':<10}"
    )

    print("-" * 90)

    for r in all_results:

        print(
            f"{r['service']:<18}"
            f"{r['avg']:<13.2f}"
            f"{r['p95']:<13.2f}"
            f"{r['success']:<12}"
            f"{r['failed']:<10}"
            f"{r['rps']:<10.2f}"
        )

    total_requests = sum(r["requests"] for r in all_results)
    total_success = sum(r["success"] for r in all_results)
    total_failed = sum(r["failed"] for r in all_results)

    print("-" * 90)
    print(f"Total Requests  : {total_requests}")
    print(f"Successful      : {total_success}")
    print(f"Failed          : {total_failed}")

    if total_requests:
        print(
            f"Success Rate    : "
            f"{total_success / total_requests * 100:.2f}%"
        )

    print("=" * 90)
    print("Performance testing completed.")


if __name__ == "__main__":
    main()
