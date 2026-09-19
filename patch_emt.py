import re

# 1. Update flight_scraper.py
with open("flight_scraper.py", "r", encoding="utf-8") as f:
    scraper_code = f.read()

# Remove the old MMT function and replace with EMT
emt_func = """def scrape_cheapest_fare_emt(page: Page, source: str, destination: str, travel_date: datetime) -> Optional[int]:
    dep_date_str = travel_date.strftime("%d/%m/%Y")
    # https://flight.easemytrip.com/FlightList/Index?srch=BLR-Bangalore-India|DEL-Delhi-India|10/10/2026&px=1-0-0&ccls=ECONOMY&rt=1
    url = f"https://flight.easemytrip.com/FlightList/Index?srch={source}-City-India|{destination}-City-India|{dep_date_str}&px=1-0-0&ccls=ECONOMY&rt=1"
    
    print(f"Scraping EaseMyTrip: {source} -> {destination} on {travel_date.strftime('%Y-%m-%d')}...")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(5000)
        
        raw_prices = page.evaluate('''() => {
            const priceDivs = Array.from(document.querySelectorAll('.txt-r6-n.exPrc'));
            return priceDivs.map(el => el.innerText);
        }''')
        
        valid_prices = []
        for p in raw_prices:
            num = clean_price_to_int(p)
            if num and 1000 <= num <= 200000:
                valid_prices.append(num)
                
        if valid_prices:
            return min(valid_prices)
    except Exception as e:
        print(f"  [Notice] Could not load EMT fares for {source}->{destination}: {e}")
    return None
"""

scraper_code = re.sub(r"def scrape_cheapest_fare_mmt.*?return None\n", emt_func, scraper_code, flags=re.DOTALL)
scraper_code = scraper_code.replace("scrape_cheapest_fare_mmt", "scrape_cheapest_fare_emt")
scraper_code = scraper_code.replace("onward_fare_mmt", "onward_fare_emt")

with open("flight_scraper.py", "w", encoding="utf-8") as f:
    f.write(scraper_code)

# 2. Update index.html
with open("index.html", "r", encoding="utf-8") as f:
    html_code = f.read()

html_code = html_code.replace("MakeMyTrip", "EaseMyTrip")
html_code = html_code.replace("MMT", "EMT")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_code)
