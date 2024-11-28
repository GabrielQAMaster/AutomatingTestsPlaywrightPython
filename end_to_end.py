import aiohttp
import asyncio
import json

# API endpoint and query parameters
API_URL = "https://datausa.io/api/data"
QUERY_PARAMS = {
    "drilldowns": "Nation",
    "measures": "Population"
}

# Output file for results
E2E_RESULTS_FILE = "e2e_test_results.txt"


async def fetch_data():
    """Fetch data from the API and validate response."""
    query_string = "&".join(f"{key}={value}" for key, value in QUERY_PARAMS.items())
    url = f"{API_URL}?{query_string}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    # Parse JSON response
                    data = await response.json()
                    return {
                        "status": "Success",
                        "status_code": response.status,
                        "data": data,
                        "validated": validate_data(data)
                    }
                else:
                    return {
                        "status": "Failure",
                        "status_code": response.status,
                        "error": f"Unexpected status code: {response.status}"
                    }
        except Exception as e:
            return {
                "status": "Failure",
                "error": str(e)
            }


def validate_data(data):
    """Perform data validation."""
    try:
        # Example validation: Check required fields
        required_keys = ["data", "source"]
        for key in required_keys:
            if key not in data:
                return False
        # Further validation can be added as needed
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False


async def e2e_test():
    """Execute the end-to-end test and save results."""
    results = await fetch_data()

    # Save results to a file
    with open(E2E_RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    # Print a summary
    if results["status"] == "Success":
        print("E2E Test Passed!")
        print(f"Data Validated: {results['validated']}")
    else:
        print("E2E Test Failed!")
        print(f"Error: {results.get('error', 'Unknown error')}")

    print(f"Results saved to {E2E_RESULTS_FILE}")


if __name__ == "__main__":
    asyncio.run(e2e_test())
