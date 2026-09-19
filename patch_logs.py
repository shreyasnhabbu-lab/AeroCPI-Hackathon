import re

with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# 1. Update trigger_scrape to log to extraction_logs
old_trigger = """def trigger_scrape(request: ScrapeRequest):
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # If the UI asks for ALL, we scrape the core prototype routes
    if request.route == "ALL":
        target_routes = ["Banglore-New Delhi", "New Delhi-Mumbai", "Mumbai-Chennai"]
    else:
        target_routes = [request.route]
        
    try:
        # Scrape all requested routes in one go
        scraped_data = run_live_scrape(target_routes)
        
        if not scraped_data:
            raise HTTPException(status_code=500, detail="Team A's scraper returned no data.")
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        saved_prices = []
        
        # Save every scraped route into the database
        for data in scraped_data:
            onward_fare = data.get("onward_fare")
            source = data.get("source")
            dest = data.get("destination")
            
            # Reverse map IATA to full name for DB consistency
            db_route = None
            if source == "BLR" and dest == "DEL": db_route = "Banglore-New Delhi"
            elif source == "DEL" and dest == "BOM": db_route = "New Delhi-Mumbai"
            elif source == "BOM" and dest == "MAA": db_route = "Mumbai-Chennai"
            
            if onward_fare and db_route:
                cursor.execute('''
                    INSERT INTO historical_prices (date, route, price) 
                    VALUES (?, ?, ?)
                ''', (today_str, db_route, onward_fare))
                saved_prices.append({"route": db_route, "price": onward_fare})
                
        conn.commit()
        conn.close()
        
        return {
            "status": "success", 
            "message": f"Real-time data captured for {len(saved_prices)} routes!",
            "date": today_str,
            "data": saved_prices
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""

new_trigger = """def trigger_scrape(request: ScrapeRequest):
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if request.route == "ALL":
        target_routes = ["Banglore-New Delhi", "New Delhi-Mumbai", "Mumbai-Chennai"]
    else:
        target_routes = [request.route]
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        scraped_data = run_live_scrape(target_routes)
        
        if not scraped_data:
            raise Exception("Team A's scraper returned no data.")
            
        saved_prices = []
        for data in scraped_data:
            onward_fare = data.get("onward_fare")
            source = data.get("source")
            dest = data.get("destination")
            
            db_route = None
            if source == "BLR" and dest == "DEL": db_route = "Banglore-New Delhi"
            elif source == "DEL" and dest == "BOM": db_route = "New Delhi-Mumbai"
            elif source == "BOM" and dest == "MAA": db_route = "Mumbai-Chennai"
            
            if onward_fare and db_route:
                cursor.execute('''
                    INSERT INTO historical_prices (date, route, price) 
                    VALUES (?, ?, ?)
                ''', (today_str, db_route, onward_fare))
                saved_prices.append({"route": db_route, "price": onward_fare})
                
        cursor.execute('''INSERT INTO extraction_logs (target_route, status, error_message) VALUES (?, ?, ?)''', (request.route, 'SUCCESS', ''))
        conn.commit()
        conn.close()
        
        return {
            "status": "success", 
            "message": f"Real-time data captured for {len(saved_prices)} routes!",
            "date": today_str,
            "data": saved_prices
        }
        
    except Exception as e:
        cursor.execute('''INSERT INTO extraction_logs (target_route, status, error_message) VALUES (?, ?, ?)''', (request.route, 'FAILURE', str(e)))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))"""

main_code = main_code.replace(old_trigger, new_trigger)

# 2. Update get_global_stats
old_stats = """    return {
        "total_fares": total_fares,
        "total_routes": total_routes,
        "success_rate": 99.8,
        "heatmap": heatmap,
        "airline_split": airline_split
    }"""

new_stats = """    cursor.execute("SELECT COUNT(*) FROM extraction_logs")
    total_attempts = cursor.fetchone()[0]
    if total_attempts > 0:
        cursor.execute("SELECT COUNT(*) FROM extraction_logs WHERE status='SUCCESS'")
        successes = cursor.fetchone()[0]
        success_rate = round((successes / total_attempts) * 100, 1)
    else:
        success_rate = 100.0

    return {
        "total_fares": total_fares,
        "total_routes": total_routes,
        "success_rate": success_rate,
        "heatmap": heatmap,
        "airline_split": airline_split
    }"""

main_code = main_code.replace(old_stats, new_stats)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
