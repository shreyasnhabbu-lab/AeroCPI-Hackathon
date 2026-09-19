from playwright.async_api import Page, Browser
from playwright_stealth import Stealth

async def get_stealth_page(playwright, proxy_config: dict = None, headless: bool = True) -> tuple[Page, Browser]:
    """
    Initializes a Chromium browser with stealth mode and optional proxy.
    Returns the page and browser objects.
    proxy_config format:
    {
        "server": "http://proxy.example.com:8080",
        "username": "user",
        "password": "password"
    }
    """
    launch_args = {
        "headless": headless,
        "args": [
            "--disable-blink-features=AutomationControlled",
        ]
    }
    if proxy_config:
        launch_args["proxy"] = proxy_config

    browser = await playwright.chromium.launch(**launch_args)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={'width': 1280, 'height': 800}
    )
    page = await context.new_page()
    await Stealth().apply_stealth_async(page)
    
    return page, browser

from playwright.sync_api import Page as SyncPage, Browser as SyncBrowser

def get_stealth_page_sync(playwright, proxy_config: dict = None, headless: bool = True) -> tuple[SyncPage, SyncBrowser]:
    """
    Synchronous version of get_stealth_page.
    """
    launch_args = {
        "headless": headless,
        "args": [
            "--disable-blink-features=AutomationControlled",
        ]
    }
    if proxy_config:
        launch_args["proxy"] = proxy_config

    browser = playwright.chromium.launch(**launch_args)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    Stealth().apply_stealth_sync(page)
    
    return page, browser
