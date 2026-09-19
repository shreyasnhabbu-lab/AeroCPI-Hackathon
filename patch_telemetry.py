import re

# 1. Update main.py
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

health_endpoint = """
@app.get("/api/system-health")
def get_system_health():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(timestamp) FROM historical_prices")
    last_sync = cursor.fetchone()[0]
    conn.close()
    
    return {
        "proxies_active": "Direct/Local",
        "ban_rate": "0%",
        "playwright_threads": 1,
        "headless_mode": "OFF (Visual)",
        "db_pending": 0,
        "last_sync": last_sync if last_sync else "Never",
        "cron_schedule": "Every 6 Hours"
    }

"""

if "/api/system-health" not in main_code:
    main_code = main_code.replace("@app.get(\"/api/routes\")", health_endpoint + "@app.get(\"/api/routes\")")
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(main_code)

# 2. Update index.html
with open("index.html", "r", encoding="utf-8") as f:
    html_code = f.read()

old_stat1 = """<h3 class="text-2xl font-bold text-slate-800">Active: 15/15</h3>
                            <p class="text-xs text-emerald-600 font-medium">Ban Rate: 0%</p>"""
new_stat1 = """<h3 id="proxyHealth" class="text-2xl font-bold text-slate-800">...</h3>
                            <p id="banRate" class="text-xs text-emerald-600 font-medium">Ban Rate: 0%</p>"""
html_code = html_code.replace(old_stat1, new_stat1)

old_stat2 = """<h3 class="text-2xl font-bold text-slate-800">8 Threads</h3>
                            <p class="text-xs text-indigo-600 font-medium">Headless Mode: ON</p>"""
new_stat2 = """<h3 id="playwrightThreads" class="text-2xl font-bold text-slate-800">...</h3>
                            <p id="headlessStatus" class="text-xs text-indigo-600 font-medium">Headless Mode: ...</p>"""
html_code = html_code.replace(old_stat2, new_stat2)

old_stat3 = """<h3 class="text-2xl font-bold text-slate-800">0 Pending</h3>
                            <p class="text-xs text-slate-400 mt-1">Last Sync: 14:30:16 IST</p>
                            <p class="text-[10px] text-slate-400">Next Batch Schedule: 02:00:00 IST (cron: daily)</p>"""
new_stat3 = """<h3 id="dbPending" class="text-2xl font-bold text-slate-800">0 Pending</h3>
                            <p id="lastSyncTime" class="text-xs text-slate-400 mt-1">Last Sync: ...</p>
                            <p id="nextBatchTime" class="text-[10px] text-slate-400">Next Batch Schedule: ...</p>"""
html_code = html_code.replace(old_stat3, new_stat3)


js_logic = """
async function fetchAdminHealth() {
    try {
        const res = await fetch('http://localhost:8000/api/system-health');
        const data = await res.json();
        
        document.getElementById('proxyHealth').innerText = data.proxies_active;
        document.getElementById('banRate').innerText = `Ban Rate: ${data.ban_rate}`;
        document.getElementById('playwrightThreads').innerText = `${data.playwright_threads} Thread`;
        document.getElementById('headlessStatus').innerText = `Headless Mode: ${data.headless_mode}`;
        document.getElementById('dbPending').innerText = `${data.db_pending} Pending`;
        
        const syncDate = new Date(data.last_sync);
        document.getElementById('lastSyncTime').innerText = `Last Sync: ${syncDate.toLocaleTimeString()}`;
        document.getElementById('nextBatchTime').innerText = `Next Batch: ${data.cron_schedule}`;
    } catch (e) {
        console.error('Failed to fetch admin health', e);
    }
}
"""

if "fetchAdminHealth" not in html_code:
    # Inject into the same interval that fetches logs
    old_interval = """setInterval(() => {
    if(!document.getElementById('adminView').classList.contains('hidden')) {
        fetchAdminLogs();
    }
}, 5000);"""
    
    new_interval = """setInterval(() => {
    if(!document.getElementById('adminView').classList.contains('hidden')) {
        fetchAdminLogs();
        fetchAdminHealth();
    }
}, 5000);"""
    
    html_code = html_code.replace(old_interval, new_interval)
    html_code = html_code.replace("</script>\n</body>", js_logic + "\n</script>\n</body>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_code)
