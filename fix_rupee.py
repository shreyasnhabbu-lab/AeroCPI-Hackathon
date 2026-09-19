import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace the specific corrupted line with the exact correct JavaScript syntax
target_regex = re.compile(r"avgElem\.innerText = '.*?' \+ Math\.round\(avgPrice\)\.toLocaleString\(\);")
replacement = "avgElem.innerText = '₹' + Math.round(avgPrice).toLocaleString();"

html = target_regex.sub(replacement, html)

# Also fix the raw data table where it might be corrupted too
target_regex2 = re.compile(r"<td class=\"px-6 py-3 font-mono font-bold text-emerald-600\">.*?\$?\{row\.price\.toLocaleString\(\)\}<\/td>")
replacement2 = "<td class=\"px-6 py-3 font-mono font-bold text-emerald-600\">₹${row.price.toLocaleString()}</td>"
html = target_regex2.sub(replacement2, html)


with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
