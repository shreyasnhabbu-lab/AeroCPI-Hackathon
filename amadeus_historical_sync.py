import os
import sqlite3
import requests
from datetime import datetime

# ==========================================
# AMADEUS FLIGHT OFFERS - HISTORICAL SYNC
# ==========================================
# This script integrates with the Amadeus ITINERARY PRICE METRICS API 
# to fetch verified historical aviation data. It safely merges into the
# existing AeroCPI database without overwriting live ixigo scraped data.

AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
DB_NAME = "aero_cpi.db"

def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def fetch_historical_prices(token, origin, destination, departure_date):
    """
    Fetches the quartile price metrics for a given route and month.
    Endpoint: ITINERARY PRICE METRICS
    """
    url = "https://test.api.amadeus.com/v1/analytics/itinerary-price-metrics"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originIataCode": origin,
        "destinationIataCode": destination,
        "departureDate": departure_date, # YYYY-MM
        "currencyCode": "INR"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 404:
        # Some routes/months may not have enough historical data in Amadeus
        return None
        
    response.raise_for_status()
    data = response.json()
    
    if "data" in data and len(data["data"]) > 0:
        # Extract the median (50th percentile) price from the metrics
        metrics = data["data"][0]["priceMetrics"]
        for metric in metrics:
            if metric["quartileRanking"] == "MEDIUM":
                return float(metric["amount"])
    return None

def sync_historical_data():
    if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
        print("Error: Amadeus API credentials not set. Please set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET environment variables.")
        return

    print("Authenticating with Amadeus...")
    token = get_amadeus_token()
    
    routes = {
        "Banglore-New Delhi": ("BLR", "DEL"),
        "New Delhi-Mumbai": ("DEL", "BOM"),
        "Mumbai-Chennai": ("BOM", "MAA")
    }
    
    # Example: Syncing historical data for the year 2019 (Base Year)
    months_to_sync = [f"2019-{str(month).zfill(2)}" for month in range(1, 13)]
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    for route_name, (origin, dest) in routes.items():
        print(f"\nFetching data for {route_name}...")
        
        for month in months_to_sync:
            # Amadeus itinerary metrics are monthly. We map the monthly average to the 1st of the month.
            db_date = f"{month}-01"
            
            try:
                median_price = fetch_historical_prices(token, origin, dest, month)
                if median_price:
                    print(f"  [{month}] Median Price: ₹{median_price}")
                    
                    # Insert safely. We use a standard INSERT, but since this is historical, 
                    # we log the source as 'Amadeus' in the departure_date/timestamp column 
                    # or leave them NULL to represent historical monthly aggregates.
                    cursor.execute('''
                        INSERT INTO historical_prices (date, route, price, class_type, departure_date, timestamp)
                        VALUES (?, ?, ?, 'economy', NULL, 'AMADEUS_API_SYNC')
                    ''', (db_date, route_name, median_price))
                else:
                    print(f"  [{month}] No data available.")
                    
            except Exception as e:
                print(f"  [{month}] API Error: {str(e)}")
                
    conn.commit()
    conn.close()
    print("\nSync Complete. SQLite database updated.")

if __name__ == "__main__":
    sync_historical_data()
