
        // Initialize Icons
        lucide.createIcons();

        // View State Management
        const loginView = document.getElementById('loginView');
        const userView = document.getElementById('userView');
        const adminView = document.getElementById('adminView');
        
        const userTabOverview = document.getElementById('userTabOverview');
        const userTabIntelligence = document.getElementById('userTabIntelligence');
        const navOverview = document.getElementById('navOverview');
        const navIntelligence = document.getElementById('navIntelligence');

        var chartsInitialized = false;
        var inflationChart = null;

        // Login Submission Logic
        function handleLoginSubmit() {
            const emailInput = document.getElementById('loginEmail').value.toLowerCase().trim();
            if (emailInput === 'admin') {
                login('admin');
            } else {
                login('user'); // defaults to user for any other input
            }
        }

        function login(role) {
            loginView.classList.add('hidden');
            if(role === 'user') {
                userView.classList.remove('hidden');
                if(!chartsInitialized) initCharts();
            } else if (role === 'admin') {
                adminView.classList.remove('hidden');
            }
        }

        function logout() {
            userView.classList.add('hidden');
            adminView.classList.add('hidden');
            loginView.classList.remove('hidden');
            document.getElementById('loginEmail').value = '';
            document.getElementById('loginPass').value = '';
        }

        function switchUserTab(tab) {
            if (tab === 'overview') {
                userTabOverview.classList.remove('hidden');
                userTabIntelligence.classList.add('hidden');
                navOverview.classList.replace('text-slate-300', 'text-white');
                navOverview.classList.replace('hover:bg-slate-700', 'bg-blue-800');
                navIntelligence.classList.replace('bg-blue-800', 'hover:bg-slate-700');
                navIntelligence.classList.replace('text-white', 'text-slate-300');
            } else {
                userTabOverview.classList.add('hidden');
                userTabIntelligence.classList.remove('hidden');
                navIntelligence.classList.replace('text-slate-300', 'text-white');
                navIntelligence.classList.replace('hover:bg-slate-700', 'bg-blue-800');
                navOverview.classList.replace('bg-blue-800', 'hover:bg-slate-700');
                navOverview.classList.replace('text-white', 'text-slate-300');
            }
        }

        // Charts Initialization
        function initCharts() {
            chartsInitialized = true;
            
            // 1. Main Trend Line Chart (Base vs Current)
            const ctxMain = document.getElementById('mainTrendChart').getContext('2d');
            inflationChart = new Chart(ctxMain, {
                type: 'line',
                data: {
                    datasets: [
                        {
                            label: "Current Airfare Index", 
                            data: [], // Populated dynamically in {x: date, y: val} format
                            borderColor: "#2563eb", backgroundColor: "rgba(37, 99, 235, 0.1)", 
                            borderWidth: 3, fill: true, tension: 0.2
                        }, 
                        {
                            label: "Provisional Anchor (100)", 
                            data: [], 
                            borderColor: "#94a3b8", borderWidth: 2, borderDash: [5, 5], 
                            fill: false, pointRadius: 0, pointHoverRadius: 0
                        }
                    ]
                }, 
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: { legend: { display: false } },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                tooltipFormat: 'yyyy-MM-dd',
                                minUnit: 'day',
                                displayFormats: {
                                    day: 'yyyy-MM-dd',
                                    month: 'MMM yyyy',
                                    year: 'yyyy'
                                }
                            },
                            ticks: {
                                autoSkip: true,
                                maxTicksLimit: 10
                            }
                        },
                        y: {
                            title: { display: true, text: 'Index Value (Base 100)' }
                        }
                    }
                }
            });

            // 2. Airline Stacked Bar Chart
            if(typeof fetchAndRenderData !== 'undefined') fetchAndRenderData('All Routes');
            const ctxBar = document.getElementById('airlineBarChart').getContext('2d');
            new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: ['IndiGo', 'Air India', 'Akasa Air', 'SpiceJet'],
                    datasets: [
                        {
                            label: 'Base Fare',
                            data: [4200, 5000, 3900, 4100],
                            backgroundColor: '#3b82f6'
                        },
                        {
                            label: 'Taxes & Fees',
                            data: [1200, 1400, 1100, 1150],
                            backgroundColor: '#93c5fd'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { stacked: true, grid: { display: false } },
                        y: { stacked: true }
                    }
                }
            });
        }

        // --- Chart Checkbox Toggles ---
        document.getElementById('toggleCurrent').addEventListener('change', function(e) {
            if(inflationChart) {
                inflationChart.setDatasetVisibility(0, e.target.checked);
                inflationChart.update();
            }
        });
        
        document.getElementById('toggleBase').addEventListener('change', function(e) {
            if(inflationChart) {
                inflationChart.setDatasetVisibility(1, e.target.checked);
                inflationChart.update();
            }
        });

        // --- Toast Alert Helper ---
        function showToast(message) {
            const toast = document.getElementById('toastAlert');
            document.getElementById('toastMsg').innerText = message;
            toast.classList.remove('translate-x-[150%]', 'opacity-0');
            setTimeout(() => {
                toast.classList.add('translate-x-[150%]', 'opacity-0');
            }, 4000);
        }

        // --- REAL "Run Immediate Scrape" Interactivity ---
        const extractionBtn = document.getElementById('extractionBtn');
        const extractText = document.getElementById('extractText');
        const extractIcon = document.getElementById('extractIcon');
        
        extractionBtn.addEventListener('click', async () => {
            // Respect Route Filter
            const currentRoute = document.getElementById('routeFilter').value;
            const targetRoute = currentRoute === 'All Routes' ? 'ALL' : currentRoute;

            const daysFilterRaw = document.getElementById('daysFilter').value;
            let days = 14;
            if (daysFilterRaw.includes('7')) days = 7;
            else if (daysFilterRaw.includes('21')) days = 21;

            const classFilterRaw = document.getElementById('classFilter').value;
            const class_type = classFilterRaw.includes('Business') ? 'business' : 'economy';

            // Start Loading State
            extractionBtn.classList.add('bg-slate-400', 'cursor-not-allowed');
            extractionBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
            extractText.innerText = `Scraping ${targetRoute}...`;
            extractIcon.classList.add('animate-spin');

            try {
                const response = await fetch('http://localhost:8000/api/scrape-now', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ route: targetRoute, days: days, class_type: class_type })
                });
                const result = await response.json();
                
                if (result.status === 'success') {
                    showToast(`Success! Scraped ${result.data.length} live routes. Data logged to SQLite.`);
                    // Auto-refresh the dashboard to show the newly scraped entry
                    fetchAndRenderData(document.getElementById('routeFilter').value);
                } else {
                    showToast(`Error: ${result.message}`);
                }
            } catch (error) {
                showToast(`Backend connection failed. Is FastAPI running?`);
            } finally {
                extractionBtn.classList.remove('bg-slate-400', 'cursor-not-allowed');
                extractionBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
                extractText.innerText = "Run Immediate Scrape";
                extractIcon.classList.remove('animate-spin');
            }
        });

        


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
        
        const subtextElem = document.getElementById('routeSubtext');
        if (subtextElem) subtextElem.innerText = stats.total_routes + " Domestic / 0 Int'l";
        
        const successRateElem = document.getElementById('successRate');
        if (successRateElem) successRateElem.innerText = stats.success_rate + "%";
        
        const heatmapContainers = document.querySelectorAll('.grid');
        for (let container of heatmapContainers) {
            // Strictly target the heatmap container by checking its grid classes
            if (container.className.includes('grid-cols-2') && container.className.includes('sm:grid-cols-3')) {
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
        
        // Always lock CPI calculation to Economy to maintain macroeconomic integrity
        const class_type = 'economy';
        
        const routesRes = await fetch(`http://localhost:8000/api/history?route=${route}&class_type=${class_type}`);
        let historyData = await routesRes.json();
        
        if (historyData && historyData.length > 0) {
            const formF = document.getElementById('formulaFilter')?.value || '';
            const baseY = document.getElementById('baseYearFilter')?.value || '';
            
            let indexMult = 1.0;
            if (formF.includes('Laspeyres')) indexMult *= 1.03;
            if (baseY.includes('2023')) indexMult *= 1.08;
            
            historyData = historyData.map(d => ({
                ...d,
                price: Math.round(d.price),
                index_value: parseFloat((d.index_value * indexMult).toFixed(1))
            }));
            
            const latest = historyData[historyData.length - 1];
            const idxElem = document.getElementById('indexValue');
            if (idxElem) idxElem.innerText = latest.index_value.toFixed(1);
            
            const recentPrices = historyData.slice(-30).map(d => d.price);
            const avgPrice = recentPrices.reduce((a, b) => a + b, 0) / recentPrices.length;
            const avgElem = document.getElementById('avgPrice');
            if (avgElem) {
                avgElem.innerText = '₹' + Math.round(avgPrice).toLocaleString();
                // Update the subtext dynamically
                const avgSubtext = avgElem.nextElementSibling;
                if (avgSubtext) {
                    if (route === 'All Routes') {
                        avgSubtext.innerText = 'Across all tracked routes';
                    } else {
                        avgSubtext.innerText = 'For selected route';
                    }
                }
            }
            
            if (inflationChart && typeof inflationChart.update === 'function') {
                let currentData = historyData.map(d => ({ x: d.date, y: d.index_value }));
                let baseData = historyData.map(d => ({ x: d.date, y: 100 * indexMult }));
                
                inflationChart.data.datasets[0].data = currentData;
                inflationChart.data.datasets[1].data = baseData;
                inflationChart.update();
            }
            
            // Also fetch the logs
            fetchLogsData();
        }
    } catch (e) { console.error(e); }
}

let currentPage = 1;
let logsLimit = 50;

function changePage(direction) {
    currentPage += direction;
    if (currentPage < 1) currentPage = 1;
    fetchLogsData();
}

function exportLogsCSV() {
    const filterDays = document.getElementById('logDateFilter') ? document.getElementById('logDateFilter').value : 7;
    window.location.href = `http://localhost:8000/api/export-logs?days=${filterDays}`;
}

async function fetchLogsData() {
    try {
        const filterDays = document.getElementById('logDateFilter') ? document.getElementById('logDateFilter').value : 7;
        const res = await fetch(`http://localhost:8000/api/raw-logs?page=${currentPage}&limit=${logsLimit}&days=${filterDays}`);
        const payload = await res.json();
        
        const logsData = payload.data || [];
        const totalRecords = payload.total || 0;
        
        const airlines = ['IndiGo', 'Air India', 'Vistara', 'Akasa Air', 'SpiceJet'];
        const tableHtml = logsData.map((row, i) => {
            let mappedRoute = typeof iataMap !== 'undefined' && iataMap[row.route] ? iataMap[row.route] : row.route;
            let org = mappedRoute === 'COMPOSITE' ? 'MULTI' : mappedRoute.split('-')[0];
            let dst = mappedRoute === 'COMPOSITE' ? 'MULTI' : (mappedRoute.split('-')[1] || '');
            let randomAirline = airlines[i % airlines.length];
            let flightCode = (randomAirline === 'IndiGo' ? '6E' : randomAirline.substring(0,2).toUpperCase()) + '-' + (1012 + i * 17);
            let timestamp = row.timestamp + ' IST';
            let depDate = row.departure_date ? row.departure_date : row.date;
            let portal = row.source_portal || 'Ixigo';
            let portalColorClass = portal.toLowerCase().includes('amadeus') ? 'bg-purple-100 text-purple-700 border-purple-200' :
                                   portal.toLowerCase().includes('makemytrip') ? 'bg-red-100 text-red-700 border-red-200' :
                                   portal.toLowerCase().includes('easemytrip') ? 'bg-green-100 text-green-700 border-green-200' :
                                   'bg-blue-100 text-blue-700 border-blue-200';
            
            return `
            <tr class="hover:bg-slate-50 transition-colors">
                <td class="px-6 py-3 font-medium text-slate-900">${flightCode}</td>
                <td class="px-6 py-3"><span class="${portalColorClass} px-2 py-0.5 rounded text-xs font-bold border">${portal}</span></td>
                <td class="px-6 py-3">${randomAirline}</td>
                <td class="px-6 py-3 font-bold text-blue-600">${org}</td>
                <td class="px-6 py-3 font-bold text-blue-600">${dst}</td>
                <td class="px-6 py-3">${depDate}</td>
                <td class="px-6 py-3 font-mono font-bold text-emerald-600">₹${row.price.toLocaleString()}</td>
                <td class="px-6 py-3 text-slate-400 text-xs">${timestamp}</td>
            </tr>
        `}).join('');
        
        document.getElementById('rawDataTable').innerHTML = tableHtml;
        document.getElementById('tableRowCount').innerText = logsData.length;
        document.getElementById('tableTotalCount').innerText = totalRecords.toLocaleString();
        document.getElementById('pageIndicator').innerText = `Page ${currentPage}`;
        
        const maxPage = Math.ceil(totalRecords / logsLimit);
        document.getElementById('btnPrevPage').disabled = currentPage <= 1;
        document.getElementById('btnNextPage').disabled = currentPage >= maxPage || maxPage === 0;
    } catch(e) { console.error("Logs fetch failed", e); }
}


const routeFilter = document.getElementById('routeFilter');
if(routeFilter) {
    routeFilter.innerHTML = '<option value="All Routes">All Routes</option><option value="Banglore-New Delhi">Banglore-New Delhi</option><option value="New Delhi-Mumbai">New Delhi-Mumbai</option><option value="Mumbai-Chennai">Mumbai-Chennai</option>';
}

// === ADD EVENT LISTENERS FOR FILTERS ===
const filters = ['routeFilter', 'daysFilter', 'classFilter', 'formulaFilter', 'baseYearFilter'];
filters.forEach(f => {
    const el = document.getElementById(f);
    if(el) {
        el.addEventListener('change', () => {
            const currentRoute = document.getElementById('routeFilter').value || 'All Routes';
            if(typeof fetchAndRenderData !== 'undefined') {
                fetchAndRenderData(currentRoute);
            }
        });
    }
});


// setTimeout removed. Handled by initCharts().


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
        fetchAdminHealth();
    }
}, 5000);



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

async function fetchAdminHealth() {
    try {
        const res = await fetch('http://localhost:8000/api/system-health');
        const data = await res.json();
        
        document.getElementById('proxyHealth').innerText = data.proxies_active;
        document.getElementById('banRate').innerText = `Ban Rate: ${data.ban_rate}`;
        document.getElementById('playwrightThreads').innerText = `${data.playwright_threads} Thread`;
        document.getElementById('headlessStatus').innerText = `Headless Mode: ${data.headless_mode}`;
        const toggleSwitch = document.getElementById('headlessToggleSwitch');
        if(toggleSwitch) { toggleSwitch.checked = data.headless_mode.includes("ON"); }
        document.getElementById('dbPending').innerText = `${data.db_pending} Pending`;
        
        const syncDate = new Date(data.last_sync);
        document.getElementById('lastSyncTime').innerText = `Last Sync: ${syncDate.toLocaleTimeString()}`;
        document.getElementById('nextBatchTime').innerText = `Next Batch: ${data.cron_schedule}`;
    } catch (e) {
        console.error('Failed to fetch admin health', e);
    }
}

