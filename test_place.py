import asyncio
from playwright.async_api import async_playwright

async def test():
    url = "https://www.google.com/maps/place/Handyman+Services/data=!4m7!3m6!1s0x487607fedc9acbe7:0x56f4cd7dbcfd18fd!8m2!3d51.424614!4d-0.141585!16s%2Fg%2F11f6dqhndz!19sChIJ58ua3P4HdkgR_Rj9vH3N9FY?authuser=0&hl=en"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 1024})
        page = await context.new_page()
        print("Navigating...")
        await page.goto(url, timeout=15000)
        
        try:
            accept_btn = page.locator("button:has-text('Accept all'), button:has-text('Agree')").first
            if await accept_btn.is_visible(timeout=3000):
                print("Clicking consent...")
                await accept_btn.click()
        except Exception as e:
            print("Consent error:", e)
            
        print("Waiting for address...")
        try:
            addr_btn = page.locator('button[data-item-id="address"]')
            await addr_btn.wait_for(timeout=5000)
            aria = await addr_btn.get_attribute('aria-label')
            text = await addr_btn.inner_text()
            print("Aria:", aria)
            print("Text:", text)
        except Exception as e:
            print("Error finding address:", e)
            
        await browser.close()

asyncio.run(test())
