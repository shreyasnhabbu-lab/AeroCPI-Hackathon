"""
Multi-Route Flight Price Scraper using Playwright.
Supports multiple airport pairs, flexible future departure dates,
resilient price extraction, and automated CSV reporting.
"""

import argparse
import csv
from datetime import datetime, timedelta
import os
import re
import sys
import time
from typing import Dict, List, Optional, Tuple

from playwright.sync_api import Page, sync_playwright
from db_manager import init_db, save_airfare
from stealth_browser import get_stealth_page_sync

DEFAULT_ROUTE_LIST = [
    ("BLR", "DEL"),
    ("DEL", "BOM"),
    ("BOM", "MAA")
]


def clean_price_to_int(price_str: str) -> Optional[int]:
    """
    Cleans currency strings (e.g. '₹8,268', 'Rs. 10,500') into an integer.
    """
    if not price_str:
        return None
    cleaned = re.sub(r"[^\d]", "", price_str)
    return int(cleaned) if cleaned else None


def get_target_date(days_ahead: int = 21):
    """
    Calculates the target travel date exactly `days_ahead` days from today.
    """
    return (datetime.today() + timedelta(days=days_ahead)).date()


def scrape_cheapest_fare(
    page: Page,
    source: str,
    destination: str,
    travel_date: datetime,
    return_date: Optional[datetime] = None,
    class_type: str = "e"
) -> Tuple[Optional[int], Optional[int]]:
    """
    Navigates to Ixigo for the route and date, waits for dynamic DOM,
    and extracts the lowest fare integer.
    """
    dep_date_str = travel_date.strftime("%d%m%Y")

    # Build Ixigo query URL
    if return_date:
        ret_date_str = return_date.strftime("%d%m%Y")
        url = f"https://www.ixigo.com/search/result/flight?from={source}&to={destination}&date={dep_date_str}&returnDate={ret_date_str}&adults=1&children=0&infants=0&class={class_type}&source=Search%20Form"
    else:
        url = f"https://www.ixigo.com/search/result/flight?from={source}&to={destination}&date={dep_date_str}&returnDate=&adults=1&children=0&infants=0&class={class_type}&source=Search%20Form"

    print(f"Scraping Ixigo: {source} -> {destination} on {travel_date.strftime('%Y-%m-%d')}...")

    try:
        # Navigate and wait for network to settle to handle anti-bot captchas or loading screens
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        
        # Explicitly wait for flight result cards to render dynamically (Ixigo typically uses robust class names or buttons)
        try:
            page.wait_for_selector("button:has-text('Book')", timeout=60000)
        except Exception:
            print(f"Warning: No 'Book' buttons found within 35 seconds. Page might be empty or CAPTCHA blocked.")

        # Extract prices strictly from flight cards (by finding 'Book' buttons) to avoid the Date Calendar slider
        raw_flights = page.evaluate("""() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const bookButtons = buttons.filter(b => b.innerText && b.innerText.trim().toUpperCase() === 'BOOK');
            
            const results = [];
            for (let btn of bookButtons) {
                // Traverse up dynamically to find the flight card container.
                // A single flight card will only have exactly 1 'BOOK' button.
                // If we hit a container with multiple 'BOOK' buttons, we've gone too far (hit the list container).
                let card = btn;
                let text = '';
                while (card.parentElement) {
                    card = card.parentElement;
                    let innerButtons = Array.from(card.querySelectorAll('button'));
                    let bookCount = innerButtons.filter(b => b.innerText && b.innerText.trim().toUpperCase() === 'BOOK').length;
                    if (bookCount > 1) {
                        break;
                    }
                    text = card.innerText || '';
                }
                
                if (text) {
                    
                    // Find ALL prices in the card to avoid grabbing a crossed-out original price instead of the discounted one
                    let price_str = null;
                    let all_prices = [];
                    const matches = [...text.matchAll(/(?:₹|INR)\\s*([\\d,]+)/g)];
                    for (let m of matches) {
                        let val = parseInt(m[1].replace(/,/g, ''), 10);
                        // Filter out 'Lock Price' fees and Promo discount text which are typically < 2000 INR.
                        // Actual commercial flight tickets on these routes are > 2000 INR (taxes alone are ~1200).
                        if (val >= 2000) {
                            all_prices.push(val);
                        }
                    }
                    if (all_prices.length > 0) {
                        price_str = Math.min(...all_prices).toString();
                    } else {
                        let numMatch = text.match(/[1-9]\\d{0,2}(?:,\\d{3})+/);
                        if (numMatch && parseInt(numMatch[0].replace(/,/g, ''), 10) >= 2000) {
                            price_str = numMatch[0];
                        }
                    }
                    
                    if (price_str) {
                        let airline = "Unknown";
                        if (text.match(/IndiGo/i)) airline = "IndiGo";
                        else if (text.match(/Air[- ]?India Exp/i)) airline = "Air India Express";
                        else if (text.match(/Air[- ]?India/i)) airline = "Air India";
                        else if (text.match(/Vistara/i)) airline = "Vistara";
                        else if (text.match(/Akasa/i)) airline = "Akasa Air";
                        else if (text.match(/SpiceJet/i)) airline = "SpiceJet";
                        
                        let flight_code = "Unknown";
                        let fcMatches = [...text.matchAll(/\\b([A-Z0-9]{2})[-\\s]?(\\d{3,4})\\b/gi)];
                        if (fcMatches.length > 0) {
                            // Map all found flight legs and join them
                            flight_code = fcMatches.map(m => m[1].toUpperCase() + '-' + m[2]).join(', ');
                        }
                        
                        results.push({
                            price: price_str,
                            airline: airline,
                            flight_code: flight_code
                        });
                    }
                }
            }
            return results;
        }""")

        valid_flights = []
        for f in raw_flights:
            num = clean_price_to_int(f['price'])
            if num and 1000 <= num <= 200000:
                valid_flights.append({
                    "price": num,
                    "airline": f['airline'],
                    "flight_code": f['flight_code']
                })

        onward_flight = min(valid_flights, key=lambda x: x['price']) if valid_flights else None

    except Exception as e:
        print(f"  [Notice] Could not load fares for {source}->{destination}: {e}")
        onward_flight = None

    return_flight = onward_flight if return_date else None
    return onward_flight, return_flight



def scrape_cheapest_fare_emt(page: Page, source: str, destination: str, travel_date: datetime, class_type: str = "e") -> Optional[dict]:
    dep_date_str = travel_date.strftime("%d/%m/%Y")
    emt_class = "BUSINESS" if class_type.lower() == "b" else "ECONOMY"
    # https://flight.easemytrip.com/FlightList/Index?srch=BLR-Bangalore-India|DEL-Delhi-India|10/10/2026&px=1-0-0&ccls=ECONOMY&rt=1
    url = f"https://flight.easemytrip.com/FlightList/Index?srch={source}-City-India|{destination}-City-India|{dep_date_str}&px=1-0-0&ccls={emt_class}&rt=1"
    
    print(f"Scraping EaseMyTrip: {source} -> {destination} on {travel_date.strftime('%Y-%m-%d')}...")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        # Wait dynamically for flight prices to appear instead of a blind timeout
        page.wait_for_selector('.txt-r6-n.exPrc', timeout=60000)
        
        raw_flights = page.evaluate('''() => {
            const priceDivs = Array.from(document.querySelectorAll('.txt-r6-n.exPrc'));
            const results = [];
            for (let div of priceDivs) {
                // Traverse up to find the flight container (typically .f-lst in EMT)
                let card = div.closest('.f-lst') || div.parentElement.parentElement.parentElement.parentElement;
                if (card) {
                    let text = card.innerText || '';
                    let price_str = div.innerText;
                    
                    let airline = "Unknown";
                    if (text.match(/IndiGo/i)) airline = "IndiGo";
                    else if (text.match(/Air[- ]?India Exp/i)) airline = "Air India Express";
                    else if (text.match(/Air[- ]?India/i)) airline = "Air India";
                    else if (text.match(/Vistara/i)) airline = "Vistara";
                    else if (text.match(/Akasa/i)) airline = "Akasa Air";
                    else if (text.match(/SpiceJet/i)) airline = "SpiceJet";
                    
                    let flight_code = "Unknown";
                    let fcMatches = [...text.matchAll(/\\b([A-Z0-9]{2})[-\\s]?(\\d{3,4})\\b/gi)];
                    if (fcMatches.length > 0) {
                        flight_code = fcMatches.map(m => m[1].toUpperCase() + '-' + m[2]).join(', ');
                    }
                    
                    results.push({
                        price: price_str,
                        airline: airline,
                        flight_code: flight_code
                    });
                }
            }
            return results;
        }''')
        
        valid_flights = []
        for f in raw_flights:
            num = clean_price_to_int(f['price'])
            if num and 1000 <= num <= 200000:
                valid_flights.append({
                    "price": num,
                    "airline": f['airline'],
                    "flight_code": f['flight_code']
                })
                
        if valid_flights:
            return min(valid_flights, key=lambda x: x['price'])
    except Exception as e:
        print(f"  [Notice] Could not load EMT fares for {source}->{destination}: {e}")
    return None

def run_scraper(
    routes: List[Tuple[str, str]],
    days_offsets: List[int],
    round_trip: bool = False,
    return_offset_days: int = 3,
    headless: bool = True,
    class_type: str = "e"
) -> List[Dict]:
    """
    Executes flight price extraction across all route/date combinations.
    """
    results = []
    init_db()  # Initialize the SQLite database from your infrastructure

    with sync_playwright() as p:
        for source, destination in routes:
            for offset in days_offsets:
                # Initialize fresh browser per route to prevent bot-protection crashes from ruining the session
                page, browser = get_stealth_page_sync(p, headless=headless)
                travel_date = datetime.today() + timedelta(days=offset)
                return_date = travel_date + timedelta(days=return_offset_days) if round_trip else None

                # Scrape each portal independently so one timeout doesn't kill the other
                onward_fare_ixigo = None
                onward_fare_emt = None
                
                try:
                    onward_fare_ixigo, return_fare = scrape_cheapest_fare(
                        page, source, destination, travel_date, return_date, class_type
                    )
                except Exception as e:
                    print(f"  [Ixigo Error] {source}->{destination}: {e}")
                    
                try:
                    onward_fare_emt = scrape_cheapest_fare_emt(page, source, destination, travel_date)
                except Exception as e:
                    print(f"  [EMT Error] {source}->{destination}: {e}")
                
                # Determine which portal offered the cheapest fare
                fares = []
                if onward_fare_ixigo:
                    fares.append((onward_fare_ixigo, "Ixigo Scraper"))
                if onward_fare_emt:
                    fares.append((onward_fare_emt, "EaseMyTrip Scraper"))
                    
                if fares:
                    best_fare = min(fares, key=lambda x: x[0]['price'])
                    onward_fare = best_fare[0]['price']
                    airline = best_fare[0].get('airline', 'Unknown')
                    flight_code = best_fare[0].get('flight_code', 'Unknown')
                    source_portal = best_fare[1]
                else:
                    onward_fare = None
                    airline = 'Unknown'
                    flight_code = 'Unknown'
                    source_portal = None

                entry = {
                    "source": source,
                    "destination": destination,
                    "offset_days": offset,
                    "travel_date": travel_date.strftime("%Y-%m-%d"),
                    "onward_fare": onward_fare,
                    "airline": airline,
                    "flight_code": flight_code,
                    "return_date": return_date.strftime("%Y-%m-%d") if return_date else "N/A",
                    "return_fare": return_fare if return_date else "N/A",
                    "source_portal": source_portal
                }
                results.append(entry)
                
# save_airfare removed to prevent duplicate rows. main.py handles it now.

                fare_display = f"INR {onward_fare}" if onward_fare else "Not Found"
                print(f"  -> Result: {source}->{destination} (+{offset}d, {travel_date.strftime('%Y-%m-%d')}): {fare_display}")
                browser.close()

    return results


def save_results_to_csv(results: List[Dict]) -> str:
    """
    Saves results to a timestamped CSV file in ~/Documents (and current folder).
    """
    safe_folder = os.path.expanduser("~/Documents")
    os.makedirs(safe_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fares_{timestamp}.csv"
    output_file = os.path.join(safe_folder, filename)

    if results:
        fieldnames = list(results[0].keys())
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        # Also save a copy locally in current directory for convenience
        local_copy = os.path.join(os.getcwd(), filename)
        with open(local_copy, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    return output_file


def main():
    parser = argparse.ArgumentParser(description="Multi-Route Airfare Scraper")
    parser.add_argument(
        "--days", nargs="+", type=int, default=[7, 14, 21],
        help="Offsets in days ahead (default: 7 14 21)"
    )
    parser.add_argument(
        "--routes", nargs="+",
        help="Custom routes formatted as SRC-DEST (e.g., --routes BLR-DEL DEL-BOM)"
    )
    parser.add_argument(
        "--round-trip", action="store_true",
        help="Search round trip flights instead of one-way"
    )
    parser.add_argument(
        "--headed", action="store_true",
        help="Run browser in visible mode (default: headless)"
    )
    args = parser.parse_args()

    # Determine routes
    if args.routes:
        routes = []
        for r in args.routes:
            parts = r.split("-")
            if len(parts) == 2:
                routes.append((parts[0].upper(), parts[1].upper()))
    else:
        routes = DEFAULT_ROUTE_LIST

    print("=" * 65)
    print("STARTING FLIGHT PRICE EXTRACTION")
    print(f"Routes:     {routes}")
    print(f"Day Offsets: {args.days}")
    print(f"Mode:       {'Round-Trip' if args.round_trip else 'One-Way'}")
    print("=" * 65)

    results = run_scraper(
        routes=routes,
        days_offsets=args.days,
        round_trip=args.round_trip,
        headless=not args.headed
    )

    output_path = save_results_to_csv(results)
    print("\n" + "=" * 65)
    print(f"Scraping complete! Results saved to:\n  -> {output_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
