import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace EVERYTHING between "avgElem.innerText =" and ".toLocaleString();"
html = re.sub(
    r"avgElem\.innerText =.*?toLocaleString\(\);",
    "avgElem.innerText = '₹' + Math.round(avgPrice).toLocaleString();",
    html,
    flags=re.DOTALL
)

# And for the table row
html = re.sub(
    r"<td class=\"px-6 py-3 font-mono font-bold text-emerald-600\">.*?toLocaleString\(\)\}<\/td>",
    '<td class="px-6 py-3 font-mono font-bold text-emerald-600">₹${row.price.toLocaleString()}</td>',
    html,
    flags=re.DOTALL
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
