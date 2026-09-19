from playwright.sync_api import sync_playwright
from stealth_browser import get_stealth_page_sync
import re

def clean_price(text):
    if not text: return None
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else None

def main():
    with sync_playwright() as p:
        page, browser = get_stealth_page_sync(p, headless=False)
        try:
            url = "https://flight.easemytrip.com/FlightList/Index?srch=BLR-Bangalore-India|DEL-Delhi-India|10/10/2026&px=1-0-0&ccls=ECONOMY&rt=1"
            print("Navigating to EaseMyTrip...")
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(5000)
            prices = page.evaluate('''() => {
                return Array.from(document.querySelectorAll('.txt-r6-n.exPrc')).map(e => e.innerText);
            }''')
            print("EMT Prices:", prices)
        except Exception as e:
            print("EMT ERROR:", e)
        browser.close()

main()
