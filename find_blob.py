import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.google.com/maps/search/Plumbers+in+Oldham?hl=en")
        
        try:
            accept_btn = page.locator("button:has-text('Accept all'), button:has-text('Agree')").first
            if await accept_btn.is_visible(timeout=5000):
                await accept_btn.click()
        except Exception:
            pass

        await asyncio.sleep(5)
        
        scripts = await page.locator('script').all()
        for i, script in enumerate(scripts):
            content = await script.inner_text()
            if "APP_INITIALIZATION_STATE" in content:
                with open(f"script_{i}.js", "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Found APP_INITIALIZATION_STATE in script {i}")
            if "cacheResponse" in content:
                 with open(f"script_cache_{i}.js", "w", encoding="utf-8") as f:
                    f.write(content)
                 print(f"Found cacheResponse in script {i}")

        await browser.close()

asyncio.run(test())
