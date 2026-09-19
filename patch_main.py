with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

import_stmt = "from apscheduler.schedulers.background import BackgroundScheduler\n"
if import_stmt not in content:
    content = content.replace("from datetime import datetime\n", "from datetime import datetime\n" + import_stmt)

cron_logic = """
# --- APScheduler Integration ---
def scheduled_scrape():
    print("[Cron] Starting scheduled scrape...")
    target_routes = ["Banglore-New Delhi", "New Delhi-Mumbai", "Mumbai-Chennai"]
    try:
        scraped_data = run_live_scrape(target_routes, 14, "economy")
        if not scraped_data:
            print("[Cron] No data scraped.")
            return
            
        conn = get_db_connection()
        cursor = conn.cursor()
        saved = 0
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        for data in scraped_data:
            onward_fare = data.get("onward_fare")
            source = data.get("source")
            dest = data.get("destination")
            travel_date = data.get("travel_date")
            
            db_route = None
            if source == "BLR" and dest == "DEL": db_route = "Banglore-New Delhi"
            elif source == "DEL" and dest == "BOM": db_route = "New Delhi-Mumbai"
            elif source == "BOM" and dest == "MAA": db_route = "Mumbai-Chennai"
            
            if onward_fare and db_route:
                now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                    INSERT INTO historical_prices (date, route, price, departure_date, timestamp, class_type) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (today_str, db_route, onward_fare, travel_date, now_ts, "economy"))
                saved += 1
                
        conn.commit()
        conn.close()
        print(f"[Cron] Scraped and saved {saved} routes.")
    except Exception as e:
        print(f"[Cron] Error: {e}")

@app.on_event("startup")
def startup_event():
    scheduler = BackgroundScheduler()
    # Runs every 6 hours
    scheduler.add_job(scheduled_scrape, 'interval', hours=6)
    scheduler.start()
"""

if "startup_event()" not in content:
    content += cron_logic
    
with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
