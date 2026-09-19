with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
idx = html.find('Aero<span class="text-amber-500">ADMIN')
print(html[idx-300:idx+200])
