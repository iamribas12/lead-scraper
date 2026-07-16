import asyncio
import aiohttp
import re
import urllib.parse
from bs4 import BeautifulSoup
import random
import traceback
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

class PlaywrightMapsEngine:
    def __init__(self, query, lead_limit, headless, ctx=None, log_callback=None):
        self.query = query
        self.lead_limit = lead_limit
        self.headless = headless
        self.ctx = ctx
        self.log_callback = log_callback
        self.semaphore = asyncio.Semaphore(3)

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    async def _jitter(self, page=None):
        delay = random.uniform(2, 5)
        await asyncio.sleep(delay)
        if page:
            try:
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                await page.mouse.move(x, y)
            except Exception:
                pass

    async def extract_website_data(self, url, session):
        if not url:
            return {'email': ''}
            
        emails = set()
        domain = urllib.parse.urlparse(url).netloc.replace('www.', '')
        
        try:
            async with session.get(url, timeout=15, ssl=False) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    found_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
                    emails.update([e.lower() for e in found_emails])
        except Exception:
            pass
            
        domain_emails = [e for e in emails if domain in e]
        banned_endings = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', 'example.com', 'wixpress.com', 'sentry.io', '.js', '.css')
        other_emails = [e for e in emails if domain not in e and not e.endswith(banned_endings) and not e.startswith('example@') and not e.startswith('test@')]
        all_sorted = domain_emails + other_emails
        
        return {
            'email': all_sorted[0] if all_sorted else ''
        }

    async def enrich_and_save(self, data, session, context):
        name = data['name']
        lead = {
            'Business Name': name,
            'Company Category': data.get('category', ''),
            'Full Address': data.get('address', ''),
            'Postal Code': '',
            'Contact Number': data['phone'],
            'Email Address': '',
            'Website URL': data['website']
        }
        
        async with self.semaphore:
            place_url = data.get('place_url', '')
            if not place_url:
                return lead

            page = None
            try:
                page = await context.new_page()
                detail_url = place_url + "&hl=en" if "?" in place_url else place_url + "?hl=en"
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
                try:
                    await page.goto(detail_url, timeout=30000, wait_until="domcontentloaded")
                except Exception:
                    await page.goto(detail_url, timeout=30000)
                
                try:
                    if "consent.google.com" in page.url or await page.locator("button:has-text('Accept all')").count() > 0:
                        accept_btn = page.locator("button:has-text('Accept all'), button:has-text('Agree'), button:has-text('Accept')").first
                        await accept_btn.click(timeout=3000)
                except Exception:
                    pass
                    
                locators = [
                    'button[data-item-id="address"]',
                    'div[data-item-id="address"]',
                    'button[aria-label^="Address:"]',
                    'div[aria-label^="Address:"]',
                    'button[aria-label*="Address"]',
                    '.Io6YTe.fontBodyMedium'
                ]
                
                full_address = ""
                try:
                    await page.wait_for_selector('.Io6YTe', timeout=5000)
                except Exception:
                    pass

                for selector in locators:
                    try:
                        el = page.locator(selector).first
                        if await el.count() > 0:
                            val = await el.get_attribute('aria-label') or await el.inner_text()
                            if val and len(val) > 5:
                                full_address = re.sub(r'^[a-zA-Z]+:\s*', '', val).strip()
                                break
                    except Exception:
                        continue
                
                if full_address:
                    lead['Full Address'] = full_address
                    uk_pc_regex = r'([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})'
                    pc_match = re.search(uk_pc_regex, full_address)
                    if pc_match:
                        lead['Postal Code'] = pc_match.group(0).upper()
                else:
                    try:
                        all_text = await page.inner_text('body')
                        pc_match = re.search(r'([A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2})', all_text, re.IGNORECASE)
                        if pc_match:
                            lead['Postal Code'] = pc_match.group(0).upper()
                            for line in all_text.split('\n'):
                                if pc_match.group(0) in line and len(line) > 10:
                                    lead['Full Address'] = line.strip()
                                    break
                    except Exception:
                        pass
                
                # Try to extract phone number if missing or as fallback
                phone_locators = [
                    'button[data-tooltip="Copy phone number"]',
                    'button[data-item-id^="phone:tel:"]',
                    '[aria-label^="Phone:"]',
                    'button:has-text("Phone")'
                ]
                
                for selector in phone_locators:
                    try:
                        el = page.locator(selector).first
                        if await el.count() > 0:
                            val = await el.get_attribute('aria-label') or await el.inner_text()
                            if val:
                                phone_val = re.sub(r'^[a-zA-Z]+:\s*', '', val).replace('Copy phone number', '').strip()
                                if len(phone_val) >= 7 and any(c.isdigit() for c in phone_val):
                                    lead['Contact Number'] = phone_val
                                    break
                    except Exception:
                        continue
                
                # Try to extract website if missing
                if not lead.get('Website URL'):
                    website_locators = [
                        'a[data-item-id="authority"]',
                        'a[aria-label^="Website:"]',
                        'a[data-tooltip="Open website"]'
                    ]
                    for selector in website_locators:
                        try:
                            el = page.locator(selector).first
                            if await el.count() > 0:
                                val = await el.get_attribute('href')
                                if val and 'google.com/url' not in val:
                                    lead['Website URL'] = val
                                    break
                                elif val and 'google.com/url' in val:
                                    # Sometimes google wraps the url in a redirect
                                    parsed = urllib.parse.urlparse(val)
                                    qs = urllib.parse.parse_qs(parsed.query)
                                    if 'q' in qs:
                                        lead['Website URL'] = qs['q'][0]
                                        break
                        except Exception:
                            continue
                            
            except Exception as e:
                self.log(f"⚠️ Enrichment failed for {name}: {str(e)}")
            finally:
                if page:
                    try:
                        await page.close()
                    except Exception:
                        pass
        
        if not lead['Postal Code'] and lead['Full Address']:
            pc_match = re.search(r'([A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2})', lead['Full Address'], re.IGNORECASE)
            if pc_match:
                lead['Postal Code'] = pc_match.group(0).upper()

        if lead['Website URL']:
            self.log(f"⚡ Background scraping: {lead['Website URL']}")
            try:
                extracted = await self.extract_website_data(lead['Website URL'], session)
                lead['Email Address'] = extracted['email']
            except Exception:
                pass
                
        return lead

    async def run_generator(self):
        self.log("🚀 Initializing Stealth Playwright...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless, args=['--disable-blink-features=AutomationControlled'])
                
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                ]
                
                context = await browser.new_context(
                    user_agent=random.choice(user_agents),
                    viewport={"width": 1280, "height": 1024}
                )
                page = await context.new_page()
                await Stealth().apply_stealth_async(page)
                
                url = f"https://www.google.com/maps/search/{urllib.parse.quote(self.query)}?hl=en"
                await page.goto(url)
                self.log("🌐 Opened Google Maps. Handling cookies...")
                await self._jitter(page)
                
                try:
                    accept_btn = page.locator("button:has-text('Accept all'), button:has-text('Agree')").first
                    if await accept_btn.is_visible(timeout=2000):
                        await accept_btn.click()
                        await self._jitter(page)
                except Exception:
                    pass

                self.log("📜 Extracting results directly from sidebar...")
                
                try:
                    feed = page.locator('div[aria-label^="Results for"], div[role="feed"]').first
                    await feed.wait_for(timeout=5000)
                except Exception:
                    if "/place/" in page.url:
                        self.log("✅ Single business profile found instantly. (Sidebar mode does not support this edge case).")
                    else:
                        self.log("❌ No businesses found on Google Maps for that exact query.")
                    await browser.close()
                    return

                processed_names = set()
                active_tasks = []
                yielded_count = 0
                
                async with aiohttp.ClientSession() as session:
                    scroll_attempts = 0
                    while yielded_count < self.lead_limit and scroll_attempts < 50:
                        await self._jitter(page)
                        
                        items_data = await page.evaluate('''() => {
                            let results = [];
                            let items = document.querySelectorAll('div[role="feed"] > div > div:has(a[href*="/maps/place/"])');
                            for (let item of items) {
                                let nameEl = item.querySelector('.qBF1Pd') || item.querySelector('.fontHeadlineSmall');
                                let name = nameEl ? nameEl.innerText : '';
                                if(!name) continue;
                                
                                let address = '';
                                let category = '';
                                let divs = item.querySelectorAll('.W4Efsd');
                                
                                // First pass: Try to extract category (usually right after rating or first item)
                                for (let div of divs) {
                                    let text = div.innerText;
                                    if (text && text.includes('·')) {
                                        let parts = text.split('·');
                                        if (parts.length >= 2) {
                                            if (parts[0].match(/[0-9.]+\\s*\\([0-9]+\\)/) || parts[0].includes('stars')) {
                                                // Rating is present, next part is category
                                                if (!category) category = parts[1].trim();
                                            } else {
                                                if (!category && !parts[0].includes('Open') && !parts[0].includes('Closed') && parts[0].length > 3) {
                                                    category = parts[0].trim();
                                                }
                                            }
                                        }
                                    }
                                }

                                for (let div of divs) {
                                    let text = div.innerText;
                                    if (text && text.includes('·')) {
                                        let parts = text.split('·');
                                        for (let part of parts) {
                                            let p = part.trim();
                                            // More inclusive check for address parts (city, street, or postcode)
                                            if (p.length > 5 && !p.match(/^\\+?[0-9\\s-]+$/) && !p.includes('Open') && !p.includes('Closed') && !p.includes('stars') && p !== category) {
                                                address = p.replace(/\\n/g, ' ').trim();
                                            }
                                        }
                                    }
                                }
                                // Fallback category cleanup
                                if (category) category = category.replace(/\\n/g, ' ').replace(/\\s*·.*$/, '').trim();
                                
                                let websiteEl = item.querySelector('a[data-value="Website"]') || item.querySelector('a[href^="http"]:not([href*="google.com"])');
                                let website = websiteEl ? websiteEl.href : '';
                                
                                let text = item.innerText;
                                let phoneMatch = text.match(/(?:\+?\d{1,3}\s*)?\(?\d{2,4}\)?[\s.-]*\d{3,4}[\s.-]*\d{3,4}/); 
                                let phone = phoneMatch ? phoneMatch[0] : '';
                                
                                let anchor = item.querySelector('a.hfpxzc');
                                let place_url = anchor ? anchor.href : '';
                                
                                results.push({name, category, address, website, phone, place_url});
                            }
                            return results;
                        }''')
                        
                        for data in items_data:
                            if yielded_count >= self.lead_limit:
                                break
                                
                            name = data['name']
                            if name in processed_names:
                                continue
                                
                            processed_names.add(name)
                            
                            task = asyncio.create_task(self.enrich_and_save(data, session, context))
                            active_tasks.append(task)
                            yielded_count += 1

                        if yielded_count >= self.lead_limit:
                            break
                            
                        try:
                            await feed.evaluate('node => node.scrollTop = node.scrollHeight')
                        except Exception:
                            break
                            
                        scroll_attempts += 1
                        
                        try:
                            end_indicator = page.locator("text=You've reached the end of the list").first
                            if await end_indicator.is_visible(timeout=500):
                                break
                        except Exception:
                            pass
                    
                    self.log(f"✅ Discovered {len(active_tasks)} businesses. Gathering parallel results...")
                    
                    completed = 0
                    try:
                        for task in asyncio.as_completed(active_tasks):
                            try:
                                lead = await task
                                completed += 1
                                yield completed, len(active_tasks), lead
                            except Exception as e:
                                self.log(f"⚠️ Task error: {str(e)}")
                                completed += 1
                                continue
                    except Exception:
                        pass
                        
                    await browser.close()

        except Exception as e:
            self.log(f"❌ Critical error: {e}\n{traceback.format_exc()}")
            raise e
