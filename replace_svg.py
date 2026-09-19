import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace the img tag with the stacked Lucide icons
# The target is: <img src="admin_icon.png" class="h-7 w-7 object-contain" alt="Admin Icon">
old_icon = '<img src="admin_icon.png" class="h-7 w-7 object-contain" alt="Admin Icon">'

new_icon = """<div class="relative w-7 h-7 flex items-center justify-center">
                                <i data-lucide="shield" class="absolute w-7 h-7 text-amber-500"></i>
                                <i data-lucide="plane-takeoff" class="absolute w-3 h-3 text-amber-500 mt-0.5"></i>
                            </div>"""

html = html.replace(old_icon, new_icon)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
