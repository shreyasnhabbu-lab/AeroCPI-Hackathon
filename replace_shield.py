import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace the shield-alert lucide icon with the new image
html = html.replace(
    '<i data-lucide="shield-alert" class="h-6 w-6 text-amber-500"></i>',
    '<img src="admin_icon.png" class="h-7 w-7 object-contain" alt="Admin Icon">'
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
