import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

s = html.find('function initCharts()')
e = html.find('// Tab Switch Logic')

if s != -1 and e != -1:
    new_init = """function initCharts() {
            chartsInitialized = true;
            const ctxMain = document.getElementById('mainTrendChart').getContext('2d');
            inflationChart = new Chart(ctxMain, {
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
            if(typeof fetchAndRenderData !== 'undefined') fetchAndRenderData('All Routes');
        }

        """
    html = html[:s] + new_init + html[e:]

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
