import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Loading Ixigo Flights...")
        await page.goto("https://www.ixigo.com/search/result/flight?from=BLR&to=DEL&date=01102026&returnDate=&adults=1&children=0&infants=0&class=e&source=Search%20Form")
        await page.wait_for_timeout(10000)
        html = await page.content()
        with open("ixigo.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Done Ixigo")
        await browser.close()

asyncio.run(main())
