import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace broken python escaped quotes with standard double quotes
html = html.replace("\\'", '"')

# Add fetchAndRenderData trigger
target = "const ctxBar ="
if 'fetchAndRenderData("All Routes");' not in html:
    html = html.replace(target, "if(typeof fetchAndRenderData !== 'undefined') fetchAndRenderData('All Routes');\n            " + target)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
