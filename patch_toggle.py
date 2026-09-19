import re

# 1. Update main.py
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# Add global state and endpoint
toggle_logic = """
# Global State for Scraper
HEADLESS_MODE = False

@app.post("/api/toggle-headless")
def toggle_headless():
    global HEADLESS_MODE
    HEADLESS_MODE = not HEADLESS_MODE
    return {"status": "success", "headless": HEADLESS_MODE}

"""
if "HEADLESS_MODE = False" not in main_code:
    main_code = main_code.replace("app = FastAPI(title=\"AeroCPI API\")", "app = FastAPI(title=\"AeroCPI API\")\n" + toggle_logic)

# Patch system-health to read global state
old_health = '"headless_mode": "OFF (Visual)",'
new_health = '"headless_mode": "ON (Fast)" if HEADLESS_MODE else "OFF (Visual)",'
main_code = main_code.replace(old_health, new_health)

# Patch run_live_scrape to use global state
old_scrape = 'headless=False,'
new_scrape = 'headless=HEADLESS_MODE,'
main_code = main_code.replace(old_scrape, new_scrape)
# Also just in case the previous replacement was still True
main_code = main_code.replace('headless=True,', new_scrape)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)

# 2. Update index.html
with open("index.html", "r", encoding="utf-8") as f:
    html_code = f.read()

# Add the button next to Headless Mode
old_html = '<p id="headlessStatus" class="text-xs text-indigo-600 font-medium">Headless Mode: ...</p>'
new_html = """<div class="flex items-center gap-2 mt-1">
                                <p id="headlessStatus" class="text-xs text-indigo-600 font-medium">Headless Mode: ...</p>
                                <button onclick="toggleHeadless()" class="px-2 py-[2px] text-[10px] uppercase font-bold bg-indigo-100 hover:bg-indigo-200 text-indigo-700 rounded transition-colors shadow-sm">Toggle</button>
                            </div>"""
html_code = html_code.replace(old_html, new_html)

# Add the JS logic
js_logic = """
async function toggleHeadless() {
    try {
        const res = await fetch('http://localhost:8000/api/toggle-headless', { method: 'POST' });
        if(res.ok) {
            // Instantly refresh the UI
            fetchAdminHealth();
        }
    } catch (e) {
        console.error('Failed to toggle headless mode', e);
    }
}
"""
if "toggleHeadless()" not in html_code:
    html_code = html_code.replace("async function fetchAdminHealth()", js_logic + "\nasync function fetchAdminHealth()")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_code)
