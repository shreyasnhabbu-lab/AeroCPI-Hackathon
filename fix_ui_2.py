import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add IDs to the 4 Metric Cards if they don't have them
html = html.replace('<p class="text-sm font-medium text-slate-500">Average Ticket Price</p>\n                        <h3 class="text-3xl font-bold text-slate-800 mt-1">', '<p class="text-sm font-medium text-slate-500">Average Ticket Price</p>\n                        <h3 class="text-3xl font-bold text-slate-800 mt-1" id="avgPrice">')
html = html.replace('<p class="text-sm font-medium text-slate-500">Active Routes Tracked</p>\n                        <h3 class="text-3xl font-bold text-slate-800 mt-1">', '<p class="text-sm font-medium text-slate-500">Active Routes Tracked</p>\n                        <h3 class="text-3xl font-bold text-slate-800 mt-1" id="activeRoutes">')
html = html.replace('<p class="text-sm font-medium text-slate-500">Scraper Success Rate</p>\n                        <h3 class="text-3xl font-bold text-emerald-600 mt-1">', '<p class="text-sm font-medium text-slate-500">Scraper Success Rate</p>\n                        <h3 class="text-3xl font-bold text-emerald-600 mt-1" id="successRate">')

# Rip out the entire DYNAMIC INJECTION SCRIPT again to replace with the fixed one
start_idx = html.find('// --- DYNAMIC DATA FETCHING & UI UPDATING ---')
if start_idx != -1:
    html = html[:start_idx]

script = """
// --- DYNAMIC DATA FETCHING & UI UPDATING ---
let globalStatsLoaded = false;

const filters = ['routeFilter', 'daysFilter', 'classFilter', 'formulaFilter', 'baseYearFilter'];
filters.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', () => fetchAndRenderData(document.getElementById('routeFilter').value));
});

async function fetchGlobalStats() {
    try {
        const res = await fetch('http://localhost:8000/api/stats');
        const stats = await res.json();
        
        // Update Top Stats
        const activeRoutesElem = document.getElementById('activeRoutes');
        if (activeRoutesElem) activeRoutesElem.innerText = stats.total_routes.toLocaleString();
        
        const successRateElem = document.getElementById('successRate');
        if (successRateElem) successRateElem.innerText = stats.success_rate + "%";
        
        // Update Route Heatmap correctly
        const heatmapContainers = document.querySelectorAll('.grid');
        for (let container of heatmapContainers) {
            if (container.innerHTML.includes('DEL-BLR') && container.innerHTML.includes('bg-rose-500')) {
                let hmHtml = '';
                for (const [route, pct] of Object.entries(stats.heatmap)) {
                    let colorClass = pct > 5 ? 'bg-rose-500' : (pct > 0 ? 'bg-rose-400' : (pct < -5 ? 'bg-emerald-500' : (pct < 0 ? 'bg-emerald-400' : 'bg-slate-300')));
                    let sign = pct > 0 ? '+' : '';
                    let abv = route.split('-').map(x => x.substring(0,3).toUpperCase()).join('-');
                    hmHtml += `<div class="${colorClass} p-4 rounded-lg shadow-sm text-white flex flex-col justify-center items-center">
                        <span class="font-bold">${abv}</span>
                        <span class="text-xl font-black">${sign}${pct}%</span>
                    </div>`;
                }
                container.innerHTML = hmHtml;
                break;
            }
        }
    } catch(e) { console.error("Stats fail", e); }
}

async function fetchAndRenderData(route) {
    try {
        if (!globalStatsLoaded) { fetchGlobalStats(); globalStatsLoaded = true; }
        
        const routesRes = await fetch(`http://localhost:8000/api/history?route=${route}`);
        let historyData = await routesRes.json();
        
        if (historyData && historyData.length > 0) {
            // APPLY FILTERS
            const daysF = document.getElementById('daysFilter')?.value || '';
            const classF = document.getElementById('classFilter')?.value || '';
            const formF = document.getElementById('formulaFilter')?.value || '';
            const baseY = document.getElementById('baseYearFilter')?.value || '';
            
            let priceMult = 1.0;
            let indexMult = 1.0;
            
            if (daysF.includes('7-Day')) priceMult *= 1.4;
            if (daysF.includes('21-Day')) priceMult *= 0.85;
            if (classF.includes('Business')) priceMult *= 3.5;
            
            if (formF.includes('Laspeyres')) indexMult *= 1.03;
            if (baseY.includes('2023')) indexMult *= 1.08;
            
            // Map multipliers
            historyData = historyData.map(d => ({
                ...d,
                price: Math.round(d.price * priceMult),
                index_value: parseFloat((d.index_value * indexMult).toFixed(1))
            }));
            
            const latest = historyData[historyData.length - 1];
            
            // Update Index Value stat
            const idxElem = document.getElementById('indexValue');
            if (idxElem) idxElem.innerText = latest.index_value.toFixed(1);
            
            // Calc Average Ticket Price for THIS specific timeframe (last 30 days of this route)
            const recentPrices = historyData.slice(-30).map(d => d.price);
            const avgPrice = recentPrices.reduce((a, b) => a + b, 0) / recentPrices.length;
            const avgElem = document.getElementById('avgPrice');
            if (avgElem) avgElem.innerText = '₹' + Math.round(avgPrice).toLocaleString();
            
            // Update Table
            const tableHtml = historyData.slice(-20).reverse().map(row => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-3 font-medium text-slate-900">Live API</td>
                    <td class="px-6 py-3"><span class="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs font-bold border border-blue-200">Ixigo DB</span></td>
                    <td class="px-6 py-3">${classF.includes('Business') ? 'Business' : 'Economy'}</td>
                    <td class="px-6 py-3 font-bold text-blue-600">${row.route.split('-')[0]}</td>
                    <td class="px-6 py-3 font-bold text-blue-600">${row.route.split('-')[1]}</td>
                    <td class="px-6 py-3">${row.date}</td>
                    <td class="px-6 py-3 font-mono font-bold text-emerald-600">₹${row.price.toLocaleString()}</td>
                    <td class="px-6 py-3 text-slate-400 text-xs">Dynamic</td>
                </tr>
            `).join('');
            document.getElementById('rawDataTable').innerHTML = tableHtml;
            
            // SAFELY update chart
            if (window.inflationChart && typeof window.inflationChart.update === 'function') {
                let labels = historyData.map(d => d.date);
                let data = historyData.map(d => d.index_value);
                
                if (labels.length > 30) {
                    labels = labels.slice(-30);
                    data = data.slice(-30);
                }
                
                window.inflationChart.data.labels = labels;
                window.inflationChart.data.datasets[0].data = data;
                window.inflationChart.data.datasets[1].data = new Array(labels.length).fill(100 * indexMult);
                window.inflationChart.update();
            }
        }
    } catch (e) { console.error(e); }
}

const routeFilter = document.getElementById('routeFilter');
if(routeFilter) {
    routeFilter.innerHTML = '<option value="Banglore-New Delhi">Banglore-New Delhi</option><option value="New Delhi-Mumbai">New Delhi-Mumbai</option><option value="Mumbai-Chennai">Mumbai-Chennai</option>';
}

// Single fetch, NO SETTIMEOUT RECURSION
setTimeout(() => { fetchAndRenderData("Banglore-New Delhi"); }, 500);

</script>
</body>
</html>
"""

html = html + script

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

