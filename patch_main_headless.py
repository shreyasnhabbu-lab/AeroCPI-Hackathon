import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("headless=True,", "headless=False,")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
