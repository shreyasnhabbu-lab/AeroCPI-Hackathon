import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add event listeners to all filters at the bottom of the script
script_addition = """
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
"""

# Replace the old routeFilter assignment at the end of the file with the new one that includes event listeners
old_routeFilter_code = """const routeFilter = document.getElementById('routeFilter');
if(routeFilter) {
    routeFilter.innerHTML = '<option value="All Routes">All Routes</option><option value="Banglore-New Delhi">Banglore-New Delhi</option><option value="New Delhi-Mumbai">New Delhi-Mumbai</option><option value="Mumbai-Chennai">Mumbai-Chennai</option>';
}"""

html = html.replace(old_routeFilter_code, script_addition)

# 2. Update the "Across all tracked routes" text dynamically inside fetchAndRenderData
# Find the part where avgElem is updated
old_avg_update = """            const avgElem = document.getElementById('avgPrice');
            if (avgElem) avgElem.innerText = '₹' + Math.round(avgPrice).toLocaleString();"""

new_avg_update = """            const avgElem = document.getElementById('avgPrice');
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
            }"""

html = html.replace(old_avg_update, new_avg_update)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
