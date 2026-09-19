import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Scope fix
html = html.replace('let inflationChart = null;', 'var inflationChart = null;')
html = html.replace('let chartsInitialized = false;', 'var chartsInitialized = false;')

# 2. Fix initCharts body
start = html.find('inflationChart = new Chart(ctxMain')
end = html.find('// Tab Switch Logic for Intelligence')

if start != -1 and end != -1:
    new_chart_code = """inflationChart = new Chart(ctxMain, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Current Airfare Index',
                        data: [],
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Base Year CPI (2024=100)',
                        data: [],
                        borderColor: '#94a3b8',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
            // Fetch live data now that chart is ready
            if(typeof fetchAndRenderData !== "undefined") fetchAndRenderData("All Routes");
        }

        """
    html = html[:start] + new_chart_code + html[end:]

# 3. Fix 42 Domestic
html = html.replace("42 Domestic / 12 Int'l", "3 Domestic / 0 Int'l", 1)
# Ensure the id is there
if 'id="routeSubtext"' not in html:
    html = html.replace('3 Domestic / 0 Int\'l</p>', '3 Domestic / 0 Int\'l</p>').replace('<p class="mt-3 text-xs font-medium text-indigo-600">3 Domestic', '<p class="mt-3 text-xs font-medium text-indigo-600" id="routeSubtext">3 Domestic')


# 4. Remove setTimeout
html = html.replace('setTimeout(() => { fetchAndRenderData("All Routes"); }, 500);', '// setTimeout removed.')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
