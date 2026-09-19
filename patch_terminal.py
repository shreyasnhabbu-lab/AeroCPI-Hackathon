import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace the hardcoded terminal body with an empty one that we will populate via JS
old_terminal = """<div id="terminalBody" class="p-4 font-mono text-sm text-green-400 flex-1 overflow-y-auto terminal-scroll leading-relaxed">
                        <p class="text-slate-500">Initializing AeroCPI Scraper Engine v2.4...</p>
                        <p class="text-slate-500">Loading proxy configurations... DONE</p>
                        <p>[14:28:44] INFO: Starting batch job (Domestic Routes)</p>
                        <p>[14:30:01] Fetching MMT DEL-BLR... <span class="text-emerald-400">200 OK</span></p>
                        <p>[14:30:03] Extracted 24 flights.</p>
                        <p>[14:30:04] Fetching MMT BOM-DEL... <span class="text-emerald-400">200 OK</span></p>
                        <p>[14:30:08] Extracted 31 flights.</p>
                        <p class="text-amber-400">[14:30:10] WARN: Captcha detected on AirIndia Direct. Rotating proxy...</p>
                        <p>[14:30:15] Fetching AirIndia DEL-BLR... <span class="text-emerald-400">200 OK</span></p>
                        <p>[14:30:16] Extracted 8 flights.</p>
                        <p>> <span class="cursor-blink">_</span></p>
                    </div>"""

new_terminal = """<div id="terminalBody" class="p-4 font-mono text-sm text-green-400 flex-1 overflow-y-auto terminal-scroll leading-relaxed">
                        <p class="text-slate-500">Initializing AeroCPI Scraper Engine v2.4...</p>
                        <p class="text-slate-500">Connecting to Live DB Logs...</p>
                        <div id="liveLogsContainer"></div>
                        <p>> <span class="cursor-blink">_</span></p>
                    </div>"""

if old_terminal in html:
    html = html.replace(old_terminal, new_terminal)
else:
    print("Warning: old_terminal not found")

# Add JS logic to fetch /api/raw-logs
js_logic = """
// Admin Terminal Log Fetching
async function fetchAdminLogs() {
    try {
        const res = await fetch('http://localhost:8000/api/raw-logs');
        const logs = await res.json();
        const container = document.getElementById('liveLogsContainer');
        if (container && logs && logs.length > 0) {
            let logHtml = '';
            // Display oldest to newest
            logs.reverse().forEach(log => {
                const ts = new Date(log.timestamp).toLocaleTimeString('en-US', {hour12: false});
                logHtml += `<p>[${ts}] Fetching ${log.route} (ID: ${log.rowid})... <span class="text-emerald-400">200 OK</span></p>`;
                logHtml += `<p>[${ts}] Extracted lowest fare: ₹${log.price} for departure ${log.departure_date}</p>`;
            });
            container.innerHTML = logHtml;
            // auto scroll
            const terminal = document.getElementById('terminalBody');
            terminal.scrollTop = terminal.scrollHeight;
        }
    } catch (e) {
        console.error('Failed to fetch admin logs', e);
    }
}

// Ensure logs fetch when switching to admin tab or periodically
setInterval(() => {
    if(!document.getElementById('adminView').classList.contains('hidden')) {
        fetchAdminLogs();
    }
}, 5000);
"""

# Inject before closing script tag
if "fetchAdminLogs" not in html:
    html = html.replace("</script>\n</body>", js_logic + "\n</script>\n</body>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
