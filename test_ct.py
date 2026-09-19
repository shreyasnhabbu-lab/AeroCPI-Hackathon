from playwright.sync_api import sync_playwright
from stealth_browser import get_stealth_page_sync

def main():
    with sync_playwright() as p:
        page, browser = get_stealth_page_sync(p, headless=False)
        try:
            url = "https://www.cleartrip.com/flights/results?adults=1&childs=0&infants=0&class=Economy&depart_date=10/10/2026&from=BLR&to=DEL"
            print("Navigating to Cleartrip...")
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            print("Cleartrip SUCCESS")
            page.wait_for_timeout(5000)
        except Exception as e:
            print("Cleartrip ERROR:", e)
        browser.close()

main()
