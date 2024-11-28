import asyncio
from playwright.async_api import async_playwright
import json

# API endpoint for testing
API_URL = "https://datausa.io/api/data"
QUERY_PARAMS = {
    "drilldowns": "Nation",
    "measures": "Population"
}

# Output file
RESULT_FILE = "integrated_test_results.txt"

async def test_api_integration():
    async with async_playwright() as p:
        # Launch a browser instance
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Open a relevant webpage (simulated user interaction)
        print("Opening Data USA home page...")
        await page.goto("https://datausa.io/")

        # Construct the API query URL
        query_string = "&".join(f"{key}={value}" for key, value in QUERY_PARAMS.items())
        api_endpoint = f"{API_URL}?{query_string}"

        # Make the API call directly within the browser context
        print(f"Requesting data from: {api_endpoint}")
        response = await page.evaluate(
            """async (url) => {
                const res = await fetch(url);
                return {
                    status: res.status,
                    data: await res.json()
                };
            }""",
            api_endpoint
        )

        # Validate the API response
        assert response["status"] == 200, f"API responded with status {response['status']}"
        data = response["data"]

        # Simulate a user viewing data in the browser console
        print("Displaying response in the browser console...")
        await page.evaluate(f"console.log('API Response:', {json.dumps(data)})")

        # Save the results to a file
        with open(RESULT_FILE, "w", encoding="utf-8") as file:
            file.write(json.dumps(data, indent=2))
        print(f"Results saved to {RESULT_FILE}")

        await browser.close()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_api_integration())
