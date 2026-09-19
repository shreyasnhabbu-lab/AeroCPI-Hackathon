import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

dynamic_script = """
<!-- DYNAMIC INJECTION SCRIPT -->
<script>
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log("Fetching live data from backend...");
        
        // Ensure routeFilter triggers dynamic update
        const routeFilter = document.getElementById('routeFilter');
        if (routeFilter) {
            routeFilter.innerHTML = '<option value="Banglore-New Delhi">Banglore-New Delhi</option><option value="New Delhi-Mumbai">New Delhi-Mumbai</option><option value="Mumbai-Chennai">Mumbai-Chennai</option>';
            routeFilter.addEventListener('change', (e) => fetchAndRenderData(e.target.value));
        }

        async function fetchAndRenderData(route) {
            const routesRes = await fetch(`http://localhost:8000/api/history?route=${route}`);
            const historyData = await routesRes.json();
            
            if (historyData && historyData.length > 0) {
                // Update Current Index stat
                const latest = historyData[historyData.length - 1];
                document.getElementById('indexValue').innerText = latest.index_value.toFixed(1);
                
                // Update Table
                const tableHtml = historyData.slice(-20).reverse().map(row => `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="px-6 py-3 font-medium text-slate-900">Scraped</td>
                        <td class="px-6 py-3"><span class="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs font-bold border border-blue-200">Ixigo / API</span></td>
                        <td class="px-6 py-3">Multiple</td>
                        <td class="px-6 py-3 font-bold text-blue-600">${row.route.split('-')[0]}</td>
                        <td class="px-6 py-3 font-bold text-blue-600">${row.route.split('-')[1]}</td>
                        <td class="px-6 py-3">${row.date}</td>
                        <td class="px-6 py-3 font-mono font-bold text-slate-800">₹${row.price}</td>
                        <td class="px-6 py-3 text-slate-400 text-xs">Live</td>
                    </tr>
                `).join('');
                document.getElementById('rawDataTable').innerHTML = tableHtml;
                
                // Wait for Chart.js to initialize then update it
                setTimeout(() => {
                    if (window.inflationChart) {
                        window.inflationChart.data.labels = historyData.map(d => d.date);
                        window.inflationChart.data.datasets[0].data = historyData.map(d => d.index_value);
                        window.inflationChart.update();
                    }
                }, 500);
            }
        }
        
        // Initial Fetch
        fetchAndRenderData("Banglore-New Delhi");
        
    } catch (e) {
        console.error("Failed to load dynamic data", e);
    }
});
</script>
</body>
"""

if "<!-- DYNAMIC INJECTION SCRIPT -->" not in html:
    html = html.replace("</body>", dynamic_script)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Injected dynamic script into index.html")
else:
    print("Already dynamic")
