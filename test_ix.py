from stealth_browser import get_stealth_page_sync
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import json

p = sync_playwright().start()
page, browser = get_stealth_page_sync(p, headless=True)
try:
    dep_date_str = (datetime.now()+timedelta(days=14)).strftime('%d%m%Y')
    url = f'https://www.ixigo.com/search/result/flight/DEL/BOM/{dep_date_str}//1/0/0/e'
    page.goto(url, wait_until='domcontentloaded')
    page.wait_for_selector('button:has-text(\'Book\')', timeout=35000)
    js_code = '''() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const bookButtons = buttons.filter(b => b.innerText && b.innerText.trim().toUpperCase() === 'BOOK');
        const results = [];
        for(let btn of bookButtons) {
            let card = btn;
            let text = '';
            while(card.parentElement) {
                card = card.parentElement;
                let inner = Array.from(card.querySelectorAll('button'));
                let bookCount = inner.filter(b => b.innerText && b.innerText.trim().toUpperCase() === 'BOOK').length;
                if(bookCount > 1) break;
                text = card.innerText || '';
            }
            results.push(text);
        }
        return results;
    }'''
    raw = page.evaluate(js_code)
    for i, t in enumerate(raw[:5]):
        print(f'Flight {i}:', repr(t[:300].encode('utf-8')))
except Exception as e:
    print('Error:', e)
finally:
    browser.close()
    p.stop()
