import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace stat 1
html = re.sub(
    r'<h3[^>]*>Active: 15/15</h3>\s*<p[^>]*>Ban Rate: 0%</p>',
    '<h3 id="proxyHealth" class="text-2xl font-bold text-slate-800">...</h3>\n<p id="banRate" class="text-xs text-emerald-600 font-medium">Ban Rate: 0%</p>',
    html
)

# Replace stat 2
html = re.sub(
    r'<h3[^>]*>8 Threads</h3>\s*<p[^>]*>Headless Mode: ON</p>',
    '<h3 id="playwrightThreads" class="text-2xl font-bold text-slate-800">...</h3>\n<p id="headlessStatus" class="text-xs text-indigo-600 font-medium">Headless Mode: ...</p>',
    html
)

# Replace stat 3
html = re.sub(
    r'<h3[^>]*>0 Pending</h3>\s*<p[^>]*>Last Sync: 14:30:16 IST</p>\s*<p[^>]*>Next Batch Schedule: 02:00:00 IST \(cron: daily\)</p>',
    '<h3 id="dbPending" class="text-2xl font-bold text-slate-800">0 Pending</h3>\n<p id="lastSyncTime" class="text-xs text-slate-400 mt-1">Last Sync: ...</p>\n<p id="nextBatchTime" class="text-[10px] text-slate-400">Next Batch Schedule: ...</p>',
    html
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
