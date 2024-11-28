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

# Configuration
NUM_REQUESTS = 100  # Total number of requests to send
CONCURRENT_REQUESTS = 10  # Number of requests sent simultaneously

# Output file
PERFORMANCE_RESULTS_FILE = "performance_test_results.txt"


async def fetch(session, url):
    """Send a single request and measure response time."""
    start_time = time.time()
    try:
        async with session.get(url) as response:
            status = response.status
            response_time = time.time() - start_time
            data = await response.json()
            return {"status": status, "response_time": response_time, "data_size": len(json.dumps(data))}
    except Exception as e:
        response_time = time.time() - start_time
        return {"status": "Error", "response_time": response_time, "error": str(e)}


async def performance_test():
    """Run the performance test."""
    query_string = "&".join(f"{key}={value}" for key, value in QUERY_PARAMS.items())
    url = f"{API_URL}?{query_string}"
    results = []

    # Create a session
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(NUM_REQUESTS):
            tasks.append(fetch(session, url))
            if len(tasks) == CONCURRENT_REQUESTS:
                # Run tasks in batches
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
                tasks = []

        # Run any remaining tasks
        if tasks:
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

    # Save results to a file
    with open(PERFORMANCE_RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    # Print summary
    response_times = [res["response_time"] for res in results if res["status"] != "Error"]
    avg_response_time = sum(response_times) / len(response_times) if response_times else float('inf')
    print(f"Total Requests: {len(results)}")
    print(f"Successful Requests: {len(response_times)}")
    print(f"Average Response Time: {avg_response_time:.2f} seconds")
    print(f"Results saved to {PERFORMANCE_RESULTS_FILE}")


if __name__ == "__main__":
    asyncio.run(performance_test())
