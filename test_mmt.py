from playwright.sync_api import sync_playwright
from stealth_browser import get_stealth_page_sync
import time

def main():
    with sync_playwright() as p:
        print("Testing headless=False...")
        page, browser = get_stealth_page_sync(p, headless=False)
        try:
            page.goto("https://www.makemytrip.com/flight/search?itinerary=DEL-BLR-03/10/2026&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E", wait_until="commit", timeout=20000)
            print("headless=False SUCCESS")
        except Exception as e:
            print("headless=False ERROR:", e)
        browser.close()
        
        print("Testing headless=True...")
        page, browser = get_stealth_page_sync(p, headless=True)
        try:
            page.goto("https://www.makemytrip.com/flight/search?itinerary=DEL-BLR-03/10/2026&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E", wait_until="commit", timeout=20000)
            print("headless=True SUCCESS")
        except Exception as e:
            print("headless=True ERROR:", e)
        browser.close()

main()
