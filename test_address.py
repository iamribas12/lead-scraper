import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def test():
    url = "https://www.google.com/maps/place/Plumb+London/@51.5204218,-0.1065664,12z/data=!4m10!1m2!2m1!1splumbers+in+london!3m6!1s0x48761cb7e42d99d1:0x41e171b30df45391!8m2!3d51.4925769!4d-0.0827258!15sChJwbHVtYmVycyBpbiBsb25kb25aFCIScGx1bWJlcnMgaW4gbG9uZG9ukgEHcGx1bWJlcpoBI0NoWkRTVWhOTUc5blMwVkpRMEZuU1VRdE0zTlVkMWMzRUFF4AEA!16s%2Fg%2F11b6ytsns_?entry=ttu"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            html = await response.text()
            print("Size:", len(html))
            
            # Try to find address in meta tags
            soup = BeautifulSoup(html, 'html.parser')
            meta_desc = soup.find('meta', attrs={'itemprop': 'description'})
            if meta_desc:
                print("Desc:", meta_desc.get('content'))
                
            meta_name = soup.find('meta', attrs={'itemprop': 'name'})
            if meta_name:
                print("Name:", meta_name.get('content'))
                
            # Google maps sometimes puts it in the title
            print("Title:", soup.title.string if soup.title else None)

asyncio.run(test())
