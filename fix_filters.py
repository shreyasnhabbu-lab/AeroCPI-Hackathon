import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# I will replace the SECOND `const filters = ` block I injected with `const uiFilters = ` to avoid the collision!
# Let's just find my injected block:
injected = """// === ADD EVENT LISTENERS FOR FILTERS ===
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
});"""

replacement = """// === ADD EVENT LISTENERS FOR FILTERS ===
// Already handled above, safely skipping duplicate declaration."""

html = html.replace(injected, replacement)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
