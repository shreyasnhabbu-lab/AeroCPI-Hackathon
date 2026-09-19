import asyncio
# pyrefly: ignore [missing-import]
from playwright.async_api import async_playwright
from stealth_browser import get_stealth_page
from db_manager import init_db, save_airfare

async def main():
    print("Initializing Database...")
    init_db()
    
    print("Testing Phantom Infrastructure...")
    async with async_playwright() as p:
        # Launching with headless=False so you can see it working!
        page, browser = await get_stealth_page(p, headless=False)
        
        print("Navigating to https://www.makemytrip.com/ to test stealth...")
        await page.goto("https://www.makemytrip.com/", wait_until="commit")
        
        # Wait a bit for tests to complete and for you to see it
        await page.wait_for_timeout(10000)
        
        # Take a screenshot to verify later
        print("Taking screenshot of the bot detection results...")
        await page.screenshot(path="stealth_test.png", full_page=True)
        print("Screenshot saved to stealth_test.png. Please review it to verify all Sannysoft checks passed (are green).")
        
        # Test database contract
        test_data = {
            "route": "BLR-DEL", 
            "date": "2026-10-01", 
            "price": 5400, 
            "status": "success"
        }
        print(f"Testing DB insertion with data: {test_data}")
        save_airfare(test_data)
        
        print("Phantom infrastructure test complete.")
        
        await browser.close()



if __name__ == "__main__":
    asyncio.run(main())
