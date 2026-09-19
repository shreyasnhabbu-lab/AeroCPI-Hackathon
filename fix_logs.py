import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix the bug where logs is an object but we treat it as an array
old_logs_check = "if (container && logs && logs.length > 0) {"
new_logs_check = """// Handle both raw array and object with .data field
        const logArray = logs.data || logs;
        if (container && logArray && logArray.length > 0) {"""
html = html.replace(old_logs_check, new_logs_check)

old_logs_loop = "logs.reverse().forEach(log => {"
new_logs_loop = "logArray.reverse().forEach(log => {"
html = html.replace(old_logs_loop, new_logs_loop)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
