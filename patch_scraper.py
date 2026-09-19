import re

with open("flight_scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

mmt_func = """
def scrape_cheapest_fare_mmt(page: Page, source: str, destination: str, travel_date: datetime) -> Optional[int]:
    dep_date_str = travel_date.strftime("%d/%m/%Y")
    url = f"https://www.makemytrip.com/flight/search?itinerary={source}-{destination}-{dep_date_str}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E"
    
    print(f"Scraping MakeMyTrip: {source} -> {destination} on {travel_date.strftime('%Y-%m-%d')}...")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(5000)
        
        raw_prices = page.evaluate('''() => {
            const priceDivs = Array.from(document.querySelectorAll('.blackText.fontSize18, .clusterViewPrice, .priceSection .blackText'));
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
        print(f"  [Notice] Could not load MMT fares for {source}->{destination}: {e}")
    return None
"""

if "scrape_cheapest_fare_mmt" not in content:
    content = content.replace("def run_scraper(", mmt_func + "\ndef run_scraper(")

# Patch the usage inside run_scraper
old_scrape_call = """                onward_fare, return_fare = scrape_cheapest_fare(
                    page, source, destination, travel_date, return_date, class_type
                )"""

new_scrape_call = """                onward_fare_ixigo, return_fare = scrape_cheapest_fare(
                    page, source, destination, travel_date, return_date, class_type
                )
                onward_fare_mmt = scrape_cheapest_fare_mmt(page, source, destination, travel_date)
                
                fares = [f for f in [onward_fare_ixigo, onward_fare_mmt] if f is not None]
                onward_fare = min(fares) if fares else None
"""

if "onward_fare_mmt =" not in content:
    content = content.replace(old_scrape_call, new_scrape_call)
    
with open("flight_scraper.py", "w", encoding="utf-8") as f:
    f.write(content)
