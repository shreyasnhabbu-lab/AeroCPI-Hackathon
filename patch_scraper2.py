import re

with open("flight_scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove the outer initialization
old_init = """    with sync_playwright() as p:
        # Use your stealth browser infrastructure!
        page, browser = get_stealth_page_sync(p, headless=headless)

        for source, destination in routes:
            for offset in days_offsets:
                travel_date = datetime.today() + timedelta(days=offset)"""

new_init = """    with sync_playwright() as p:
        for source, destination in routes:
            for offset in days_offsets:
                # Initialize fresh browser per route to prevent bot-protection crashes from ruining the session
                page, browser = get_stealth_page_sync(p, headless=headless)
                travel_date = datetime.today() + timedelta(days=offset)"""

content = content.replace(old_init, new_init)

# Move browser.close() inside the inner loop
old_close = """                print(f"  -> Result: {source}->{destination} (+{offset}d, {travel_date.strftime('%Y-%m-%d')}): {fare_display}")

        browser.close()"""

new_close = """                print(f"  -> Result: {source}->{destination} (+{offset}d, {travel_date.strftime('%Y-%m-%d')}): {fare_display}")
                browser.close()"""

content = content.replace(old_close, new_close)

with open("flight_scraper.py", "w", encoding="utf-8") as f:
    f.write(content)
