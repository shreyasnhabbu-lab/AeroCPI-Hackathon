import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

js_logic = """
async function toggleHeadless() {
    try {
        const res = await fetch('http://localhost:8000/api/toggle-headless', { method: 'POST' });
        if(res.ok) {
            fetchAdminHealth();
        }
    } catch (e) {
        console.error('Failed to toggle headless mode', e);
    }
}
"""

if "async function toggleHeadless" not in html:
    html = html.replace("async function fetchAdminHealth()", js_logic + "\nasync function fetchAdminHealth()")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
