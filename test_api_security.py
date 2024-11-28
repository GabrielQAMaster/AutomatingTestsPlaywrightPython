import asyncio
from playwright.async_api import async_playwright
import json
import random
import string

# API endpoint for testing
API_URL = "https://datausa.io/api/data"
QUERY_PARAMS = {
    "drilldowns": "Nation",
    "measures": "Population"
}

# Output file
SECURITY_TEST_RESULTS_FILE = "security_test_results.txt"

async def test_security():
    results = {"tests": []}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Test 1: Unauthorized Access (if API requires authentication, which this API doesn't)
        print("Test 1: Unauthorized Access")
        api_endpoint = f"{API_URL}?{QUERY_PARAMS['drilldowns']}=Invalid&{QUERY_PARAMS['measures']}=Invalid"

        response = await page.evaluate(
            """async (url) => {
                const res = await fetch(url);
                return { status: res.status, data: await res.text() };
            }""",
            api_endpoint
        )
        results["tests"].append({
            "test": "Unauthorized Access",
            "endpoint": api_endpoint,
            "status": response["status"],
            "response_snippet": response["data"][:200]
        })

        print(f"Unauthorized Access Test: Status {response['status']}")

        # Test 2: Input Validation (SQL/Code Injection)
        print("Test 2: Input Validation")
        malicious_input = "' OR 1=1 --"
        injection_endpoint = f"{API_URL}?drilldowns={malicious_input}&measures={QUERY_PARAMS['measures']}"
        
        response = await page.evaluate(
            """async (url) => {
                const res = await fetch(url);
                return { status: res.status, data: await res.text() };
            }""",
            injection_endpoint
        )
        results["tests"].append({
            "test": "Input Validation (SQL/Code Injection)",
            "endpoint": injection_endpoint,
            "status": response["status"],
            "response_snippet": response["data"][:200]
        })

        print(f"Input Validation Test: Status {response['status']}")

        # Test 3: Rate Limiting
        print("Test 3: Rate Limiting")
        rate_limit_endpoint = f"{API_URL}?{QUERY_PARAMS['drilldowns']}={QUERY_PARAMS['drilldowns']}&{QUERY_PARAMS['measures']}={QUERY_PARAMS['measures']}"
        rate_limit_responses = []

        for _ in range(10):  # Send multiple rapid requests
            response = await page.evaluate(
                """async (url) => {
                    const res = await fetch(url);
                    return { status: res.status, data: await res.text() };
                }""",
                rate_limit_endpoint
            )
            rate_limit_responses.append(response["status"])
            await asyncio.sleep(0.2)  # Short delay between requests

        results["tests"].append({
            "test": "Rate Limiting",
            "endpoint": rate_limit_endpoint,
            "statuses": rate_limit_responses
        })

        print(f"Rate Limiting Test: Statuses {rate_limit_responses}")

        # Save results to a file
        with open(SECURITY_TEST_RESULTS_FILE, "w", encoding="utf-8") as file:
            file.write(json.dumps(results, indent=2))
        print(f"Security test results saved to {SECURITY_TEST_RESULTS_FILE}")

        await browser.close()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_security())
