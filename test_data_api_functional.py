import asyncio
from playwright.async_api import async_playwright
import json

# API URL and Query
API_URL = "https://datausa.io/api/data"
QUERY_PARAMS = {
    "drilldowns": "Nation",
    "measures": "Population"
}

# File to save the results
RESULT_FILE = "api_results.txt"

async def test_api():
    async with async_playwright() as p:
        # Create a browser instance (not necessary for API calls but kept for completeness)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Construct the API query URL
        query_string = "&".join(f"{key}={value}" for key, value in QUERY_PARAMS.items())
        api_endpoint = f"{API_URL}?{query_string}"

        print(f"Testing API endpoint: {api_endpoint}")
        
        # Make the API call
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

        # Validate the response
        assert response["status"] == 200, f"API responded with status {response['status']}"
        data = response["data"]

        # Save the results to a text file
        with open(RESULT_FILE, "w", encoding="utf-8") as file:
            file.write(json.dumps(data, indent=2))
        print(f"API results saved to {RESULT_FILE}")

        await browser.close()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_api())
