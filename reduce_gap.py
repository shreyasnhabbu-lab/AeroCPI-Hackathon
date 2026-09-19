with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace gap-2 with gap-1 just for that specific flex container
old = """<div class="flex items-center gap-2">
                            <div class="relative w-9 h-9 flex items-center justify-center">"""

new = """<div class="flex items-center gap-1">
                            <div class="relative w-9 h-9 flex items-center justify-center">"""

html = html.replace(old, new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
