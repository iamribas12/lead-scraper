import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.google.com/maps/search/Plumbers+in+London")
        
        try:
            accept_btn = page.locator("button:has-text('Accept all'), button:has-text('Agree')").first
            if await accept_btn.is_visible(timeout=2000):
                await accept_btn.click()
        except Exception:
            pass

        feed = page.locator('div[role="feed"]').first
        await feed.wait_for()
        
        item = page.locator('div[role="feed"] > div > div:has(a[href*="/maps/place/"])').first
        await item.wait_for()
        html = await item.inner_html()
        
        with open("item.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Done.")
        await browser.close()

asyncio.run(test())
