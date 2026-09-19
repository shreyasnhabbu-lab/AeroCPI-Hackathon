import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace the current SVG stack with a larger version
old_icon = """<div class="relative w-7 h-7 flex items-center justify-center">
                                <i data-lucide="shield" class="absolute w-7 h-7 text-amber-500"></i>
                                <i data-lucide="plane-takeoff" class="absolute w-3 h-3 text-amber-500 mt-0.5"></i>
                            </div>"""

new_icon = """<div class="relative w-9 h-9 flex items-center justify-center">
                                <i data-lucide="shield" class="absolute w-9 h-9 text-amber-500"></i>
                                <i data-lucide="plane-takeoff" class="absolute w-4 h-4 text-amber-500 mt-0.5"></i>
                            </div>"""

html = html.replace(old_icon, new_icon)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
