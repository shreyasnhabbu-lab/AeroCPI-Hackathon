import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

old_matrix = """                    <div class="p-4 space-y-4">
                        <div class="flex justify-between items-center p-3 bg-slate-50 border border-slate-100 rounded-lg">
                            <div class="flex items-center gap-3">
                                <div class="h-6 w-6 bg-red-600 rounded flex items-center justify-center text-white text-[10px] font-bold">EMT</div>
                                <span class="font-medium text-slate-700">EaseMyTrip</span>
                            </div>
                            <span class="px-2 py-1 bg-emerald-100 text-emerald-700 text-[10px] uppercase font-bold rounded">ONLINE</span>
                        </div>
                        <div class="flex justify-between items-center p-3 bg-slate-50 border border-slate-100 rounded-lg">
                            <div class="flex items-center gap-3">
                                <div class="h-6 w-6 bg-orange-500 rounded flex items-center justify-center text-white text-[10px] font-bold">CT</div>
                                <span class="font-medium text-slate-700">Cleartrip</span>
                            </div>
                            <span class="px-2 py-1 bg-emerald-100 text-emerald-700 text-[10px] uppercase font-bold rounded">ONLINE</span>
                        </div>
                        <div class="flex justify-between items-center p-3 bg-amber-50 border border-amber-100 rounded-lg">
                            <div class="flex items-center gap-3">
                                <div class="h-6 w-6 bg-orange-600 rounded flex items-center justify-center text-white text-[10px] font-bold">AI</div>
                                <span class="font-medium text-amber-900">Air India Direct</span>
                            </div>
                            <span class="px-2 py-1 bg-amber-200 text-amber-800 text-[10px] uppercase font-bold rounded flex items-center gap-1">
                                <i data-lucide="alert-triangle" class="h-3 w-3"></i> WARNING
                            </span>
                        </div>
                        <p class="text-xs text-amber-700 mt-[-10px] pl-1 font-medium bg-amber-50/50 p-2 rounded border border-amber-100">
                            DOM structure changed. Parser matching at 60%.
                        </p>
                        
                        <div class="flex justify-between items-center p-3 bg-slate-50 border border-slate-100 rounded-lg">
                            <div class="flex items-center gap-3">
                                <div class="h-6 w-6 bg-blue-800 rounded flex items-center justify-center text-white text-[10px] font-bold">6E</div>
                                <span class="font-medium text-slate-700">IndiGo Direct</span>
                            </div>
                            <span class="px-2 py-1 bg-emerald-100 text-emerald-700 text-[10px] uppercase font-bold rounded">ONLINE</span>
                        </div>
                    </div>"""

new_matrix = """                    <div class="p-4 space-y-4">
                        <div class="flex justify-between items-center p-3 bg-slate-50 border border-slate-100 rounded-lg">
                            <div class="flex items-center gap-3">
                                <div class="h-6 w-6 bg-red-600 rounded flex items-center justify-center text-white text-[10px] font-bold">EMT</div>
                                <span class="font-medium text-slate-700">EaseMyTrip</span>
                            </div>
                            <span class="px-2 py-1 bg-emerald-100 text-emerald-700 text-[10px] uppercase font-bold rounded">ONLINE</span>
                        </div>
                        <div class="flex justify-between items-center p-3 bg-slate-50 border border-slate-100 rounded-lg">
                            <div class="flex items-center gap-3">
                                <div class="h-6 w-6 bg-indigo-600 rounded flex items-center justify-center text-white text-[10px] font-bold">IX</div>
                                <span class="font-medium text-slate-700">Ixigo</span>
                            </div>
                            <span class="px-2 py-1 bg-emerald-100 text-emerald-700 text-[10px] uppercase font-bold rounded">ONLINE</span>
                        </div>
                    </div>"""

if old_matrix in html:
    html = html.replace(old_matrix, new_matrix)
else:
    print("WARNING: Matrix block not found!")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
