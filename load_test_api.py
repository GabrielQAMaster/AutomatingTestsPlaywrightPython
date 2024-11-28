import aiohttp
import asyncio
import time
import json

# API endpoint and query parameters
API_URL = "https://datausa.io/api/data"
QUERY_PARAMS = {
    "drilldowns": "Nation",
    "measures": "Population"
}

# Load test configuration
CONCURRENT_USERS = 50  # Number of simultaneous users
REQUESTS_PER_USER = 10  # Requests per user

# Output file
LOAD_TEST_RESULTS_FILE = "load_test_results.txt"

async def make_request(session, user_id, request_id):
    """Send a single request to the API."""
    query_string = "&".join(f"{key}={value}" for key, value in QUERY_PARAMS.items())
    url = f"{API_URL}?{query_string}"
    
    try:
        async with session.get(url) as response:
            status = response.status
            data = await response.json()
            print(f"User {user_id}, Request {request_id}: Status {status}")
            return {"user_id": user_id, "request_id": request_id, "status": status, "response_time": response.elapsed.total_seconds()}
    except Exception as e:
        print(f"User {user_id}, Request {request_id} failed: {e}")
        return {"user_id": user_id, "request_id": request_id, "status": "Failed", "error": str(e)}

async def load_test():
    """Run the load test with multiple users."""
    results = []
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for user_id in range(CONCURRENT_USERS):
            for request_id in range(REQUESTS_PER_USER):
                tasks.append(make_request(session, user_id, request_id))
        
        responses = await asyncio.gather(*tasks)
        results.extend(responses)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Load Test Completed in {total_time:.2f} seconds")

    # Save results to a file
    with open(LOAD_TEST_RESULTS_FILE, "w", encoding="utf-8") as file:
        file.write(json.dumps(results, indent=2))

    print(f"Results saved to {LOAD_TEST_RESULTS_FILE}")

if __name__ == "__main__":
    asyncio.run(load_test())
