FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install apscheduler uvicorn

# Playwright requires its own command to install all the complex Linux OS dependencies
# This handles all the libgconf/libnss3/libxss stuff automatically based on the exact Debian version!
RUN playwright install chromium
RUN playwright install-deps

COPY . .

# Run the application using the dynamic PORT environment variable provided by Render
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
