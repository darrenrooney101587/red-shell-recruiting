from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Setup headless browser
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# Navigate to the LinkedIn profile
profile_url = "https://www.linkedin.com/in/darren-rooney-54550065/"
driver.get(profile_url)

# Wait for JavaScript to render
time.sleep(5)  # Wait time may need tuning

# Parse rendered HTML
soup = BeautifulSoup(driver.page_source, "html.parser")
img_tag = soup.find("img", class_="profile-photo-edit__preview")

if img_tag and img_tag.get("src"):
    print("Image URL:", img_tag["src"])
else:
    print("Profile image not found.")

driver.quit()
