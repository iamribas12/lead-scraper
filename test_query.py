from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
import time

options = Options()
options.add_argument("--headless=new")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = f"https://www.google.com/maps/search/{urllib.parse.quote('Manufacturing Ltd company in AL1 Alban')}"
driver.get(url)
time.sleep(3)

print("URL:", driver.current_url)
try:
    print("Feed:", driver.find_element(By.XPATH, '//div[contains(@aria-label, "Results for") or @role="feed"]'))
except Exception as e:
    print("No feed.")
    
try:
    print("No results text:", driver.find_element(By.XPATH, '//*[contains(text(), "Google Maps can")]').text)
except Exception:
    pass

driver.quit()
