import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Fix the variable declaration to ensure it's global across script tags
html = html.replace('let inflationChart = null;', 'var inflationChart = null;')
html = html.replace('let chartsInitialized = false;', 'var chartsInitialized = false;')

# 2. Fix initCharts to call fetchAndRenderData immediately after chart creation
if 'fetchAndRenderData("All Routes");' not in html[html.find('function initCharts()'):html.find('function updateRoute(route)')]:
    html = html.replace('            });\n        }\n\n        // Tab Switch Logic for Intelligence', '            });\n            // Fetch live data now that chart is ready\n            if(typeof fetchAndRenderData !== "undefined") fetchAndRenderData("All Routes");\n        }\n\n        // Tab Switch Logic for Intelligence')

# 3. Fix the "42 Domestic" line
html = html.replace('<p class="mt-3 text-xs font-medium text-indigo-600">42 Domestic / 12 Int\'l</p>', '<p class="mt-3 text-xs font-medium text-indigo-600" id="routeSubtext">3 Domestic / 0 Int\'l</p>')

# 4. Remove the initial setTimeout that was failing silently because chart didn't exist yet
html = html.replace('setTimeout(() => { fetchAndRenderData("All Routes"); }, 500);', '// setTimeout removed. Handled by initCharts().')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
