import re

with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

serve_code = """
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# Serve the main index.html at the root URL
@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

"""

if "@app.get(\"/\")" not in main_code:
    main_code = main_code.replace("app = FastAPI(title=\"AeroCPI API\")", "app = FastAPI(title=\"AeroCPI API\")\n" + serve_code)
    
with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
