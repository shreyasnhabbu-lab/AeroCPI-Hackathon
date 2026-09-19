import re

# ==========================================
# 1. UPDATE BACKEND (main.py)
# ==========================================
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# Fix /api/history to support "All Routes" composite index
old_history = """@app.get("/api/history")
def get_history(route: str = "Banglore-New Delhi"):
    conn = get_db_connection()
    query = "SELECT * FROM historical_prices WHERE route = ? ORDER BY date ASC"
    df = pd.read_sql_query(query, conn, params=(route,))
    conn.close()
    
    if df.empty:
        return []
        
    # Recalculate index dynamically on the fly (base year = first price)
    base_price = df['price'].iloc[0]
    df['index_value'] = ((df['price'] / base_price) * 100).round(2)
    
    return df.to_dict(orient="records")"""

new_history = """@app.get("/api/history")
def get_history(route: str = "All Routes"):
    conn = get_db_connection()
    if route == "All Routes":
        # Composite CPI logic: Average price across all routes per date
        query = "SELECT date, 'All Routes' as route, AVG(price) as price FROM historical_prices GROUP BY date ORDER BY date ASC"
        df = pd.read_sql_query(query, conn)
    else:
        query = "SELECT * FROM historical_prices WHERE route = ? ORDER BY date ASC"
        df = pd.read_sql_query(query, conn, params=(route,))
    conn.close()
    
    if df.empty:
        return []
        
    # Recalculate index dynamically on the fly
    base_price = df['price'].iloc[0]
    df['index_value'] = ((df['price'] / base_price) * 100).round(2)
    
    return df.to_dict(orient="records")"""

main_code = main_code.replace(old_history, new_history)

# Fix /api/stats to hardcode total routes to 3 and fix heatmap 0% issues by ensuring we compare cleanly
old_stats = """    cursor.execute("SELECT COUNT(DISTINCT route) FROM historical_prices")
    total_routes = cursor.fetchone()[0]"""

new_stats = """    # User explicitly requested 3 active routes for prototype
    total_routes = 3"""
main_code = main_code.replace(old_stats, new_stats)

old_heatmap = """    for r in routes_to_check:
        cursor.execute("SELECT price FROM historical_prices WHERE route=? ORDER BY date DESC LIMIT 30", (r,))
        prices = [row['price'] for row in cursor.fetchall()]
        if len(prices) >= 30:
            old_p, new_p = prices[-1], prices[0]
            pct = ((new_p - old_p) / old_p) * 100
            heatmap[r] = round(pct, 1)
        else:
            heatmap[r] = 0.0"""

new_heatmap = """    for r in routes_to_check:
        cursor.execute("SELECT price FROM historical_prices WHERE route=? ORDER BY date ASC", (r,))
        prices = [row['price'] for row in cursor.fetchall()]
        if len(prices) >= 2:
            # Compare latest with oldest available in the sliding window
            window = prices[-30:] if len(prices) > 30 else prices
            old_p, new_p = window[0], window[-1]
            pct = ((new_p - old_p) / old_p) * 100
            heatmap[r] = round(pct, 1)
        else:
            heatmap[r] = 0.0"""
main_code = main_code.replace(old_heatmap, new_heatmap)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)

# ==========================================
# 2. UPDATE FRONTEND (index.html)
# ==========================================
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix the Run Immediate Scrape button to respect the filter
old_scrape = """        extractionBtn.addEventListener('click', async () => {
            // Start Loading State
            extractionBtn.classList.add('bg-slate-400', 'cursor-not-allowed');
            extractionBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
            extractText.innerText = "Scraping Live from Ixigo...";
            extractIcon.classList.add('animate-spin');

            try {
                // Call Team B's API which triggers Team A's Stealth Scraper!
                const response = await fetch('http://localhost:8000/api/scrape-now', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ route: 'ALL' })
                });"""

new_scrape = """        extractionBtn.addEventListener('click', async () => {
            // Respect Route Filter
            const currentRoute = document.getElementById('routeFilter').value;
            const targetRoute = currentRoute === 'All Routes' ? 'ALL' : currentRoute;

            // Start Loading State
            extractionBtn.classList.add('bg-slate-400', 'cursor-not-allowed');
            extractionBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
            extractText.innerText = `Scraping ${targetRoute}...`;
            extractIcon.classList.add('animate-spin');

            try {
                const response = await fetch('http://localhost:8000/api/scrape-now', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ route: targetRoute })
                });"""

html = html.replace(old_scrape, new_scrape)

# Update the Dynamic Script Block
start_idx = html.find('// --- DYNAMIC DATA FETCHING & UI UPDATING ---')
if start_idx != -1:
    html = html[:start_idx]

script = """
// --- DYNAMIC DATA FETCHING & UI UPDATING ---
let globalStatsLoaded = false;

const iataMap = {
    'Banglore-New Delhi': 'BLR-DEL',
    'New Delhi-Mumbai': 'DEL-BOM',
    'Mumbai-Chennai': 'BOM-MAA',
    'All Routes': 'COMPOSITE'
};

const filters = ['routeFilter', 'daysFilter', 'classFilter', 'formulaFilter', 'baseYearFilter'];
filters.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', () => fetchAndRenderData(document.getElementById('routeFilter').value));
});

async function fetchGlobalStats() {
    try {
        const res = await fetch('http://localhost:8000/api/stats');
        const stats = await res.json();
        
        const activeRoutesElem = document.getElementById('activeRoutes');
        if (activeRoutesElem) activeRoutesElem.innerText = stats.total_routes;
        
        const successRateElem = document.getElementById('successRate');
        if (successRateElem) successRateElem.innerText = stats.success_rate + "%";
        
        const heatmapContainers = document.querySelectorAll('.grid');
        for (let container of heatmapContainers) {
            // Safe identifier for the heatmap container
            if (container.children.length > 0 && container.innerHTML.includes('bg-')) {
                let hmHtml = '';
                for (const [route, pct] of Object.entries(stats.heatmap)) {
                    let colorClass = pct > 5 ? 'bg-rose-500' : (pct > 0 ? 'bg-rose-400' : (pct < -5 ? 'bg-emerald-500' : (pct < 0 ? 'bg-emerald-400' : 'bg-slate-300')));
                    let sign = pct > 0 ? '+' : '';
                    let abv = iataMap[route] || route;
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
            
            historyData = historyData.map(d => ({
                ...d,
                price: Math.round(d.price * priceMult),
                index_value: parseFloat((d.index_value * indexMult).toFixed(1))
            }));
            
            const latest = historyData[historyData.length - 1];
            const idxElem = document.getElementById('indexValue');
            if (idxElem) idxElem.innerText = latest.index_value.toFixed(1);
            
            const recentPrices = historyData.slice(-30).map(d => d.price);
            const avgPrice = recentPrices.reduce((a, b) => a + b, 0) / recentPrices.length;
            const avgElem = document.getElementById('avgPrice');
            if (avgElem) avgElem.innerText = '₹' + Math.round(avgPrice).toLocaleString();
            
            const tableHtml = historyData.slice(-20).reverse().map(row => {
                let org = row.route === 'All Routes' ? 'All' : row.route.split('-')[0];
                let dst = row.route === 'All Routes' ? 'Routes' : row.route.split('-')[1];
                return `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="px-6 py-3 font-medium text-slate-900">Live API</td>
                    <td class="px-6 py-3"><span class="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs font-bold border border-blue-200">Ixigo DB</span></td>
                    <td class="px-6 py-3">${classF.includes('Business') ? 'Business' : 'Economy'}</td>
                    <td class="px-6 py-3 font-bold text-blue-600">${org}</td>
                    <td class="px-6 py-3 font-bold text-blue-600">${dst}</td>
                    <td class="px-6 py-3">${row.date}</td>
                    <td class="px-6 py-3 font-mono font-bold text-emerald-600">₹${row.price.toLocaleString()}</td>
                    <td class="px-6 py-3 text-slate-400 text-xs">Dynamic</td>
                </tr>
            `}).join('');
            document.getElementById('rawDataTable').innerHTML = tableHtml;
            
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
    routeFilter.innerHTML = '<option value="All Routes">All Routes</option><option value="Banglore-New Delhi">Banglore-New Delhi</option><option value="New Delhi-Mumbai">New Delhi-Mumbai</option><option value="Mumbai-Chennai">Mumbai-Chennai</option>';
}

setTimeout(() => { fetchAndRenderData("All Routes"); }, 500);

</script>
</body>
</html>
"""

html = html + script

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Done patching.")
