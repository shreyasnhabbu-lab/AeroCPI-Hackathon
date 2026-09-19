import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

old_html = """<div class="flex items-center gap-2 mt-1">
                                <p id="headlessStatus" class="text-xs text-indigo-600 font-medium">Headless Mode: ...</p>
                                <button onclick="toggleHeadless()" class="px-2 py-[2px] text-[10px] uppercase font-bold bg-indigo-100 hover:bg-indigo-200 text-indigo-700 rounded transition-colors shadow-sm">Toggle</button>
                            </div>"""

new_html = """<div class="flex items-center gap-2 mt-1">
                                <p id="headlessStatus" class="text-xs text-indigo-600 font-medium">Headless Mode: ...</p>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" id="headlessToggleSwitch" class="sr-only peer" onchange="toggleHeadless()">
                                    <div class="w-8 h-4 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-4 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-indigo-600"></div>
                                </label>
                            </div>"""

html = html.replace(old_html, new_html)

old_js = "document.getElementById('headlessStatus').innerText = `Headless Mode: ${data.headless_mode}`;"
new_js = """document.getElementById('headlessStatus').innerText = `Headless Mode: ${data.headless_mode}`;
        const toggleSwitch = document.getElementById('headlessToggleSwitch');
        if(toggleSwitch) { toggleSwitch.checked = data.headless_mode.includes("ON"); }"""

html = html.replace(old_js, new_js)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
