# Fetches yunzhan365.com book contents and saves it to PDF.
# Really slow but I just wanted to make this work in any way.
# Third-party modules: requests, selenium, pillow
# Usage: python yunzhan.py <needed yunzhan book url>


from io import BytesIO
from json import dumps, loads
from math import floor
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from sys import argv
from time import sleep, time
from PIL import Image
from selenium.webdriver.chrome.service import Service

if __name__ == "__main__":

    LINK = argv[1] if len(argv) > 1 else input("Link: ")

    if "yunzhan365.com/basic/" in LINK:
        print("Fixing the URL...")
        soup = BeautifulSoup(requests.get(LINK).text, "html.parser")
        book_info = soup.find("div", { "class": "book-info" })
        title = book_info.find("h1", { "class": "title" })
        LINK = title.find("a").get("href")
        print("Fixed to " + LINK)
  
    desired_capabilities = DesiredCapabilities.CHROME 
    desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"} 
  
    options = webdriver.ChromeOptions()
    options.add_argument('headless') 
    options.add_argument("--ignore-certificate-errors") 
    options.add_argument("--log-level=3")
  
    service = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(LINK)
    sleep(5)

    NUM_PAGES = driver.execute_script("return originTotalPageCount;")

    flips = floor((NUM_PAGES - 3) / 2)
    if flips > 0:
        for i in range(flips):
            print("Fetching pages " + str(5 + 2 * i) + "/" + str(NUM_PAGES) + "...", end="\r")
            driver.execute_script("nextPageFun(\"mouse wheel flip\")")
            sleep(0.5)

    print("\nWriting the network log...")
    logs = driver.get_log("performance")
    with open("network_log.json", "w", encoding="utf-8") as f: 
        f.write("[") 
        for log in logs: 
            network_log = loads(log["message"])["message"] 
            if("Network.response" in network_log["method"] or "Network.request" in network_log["method"] or "Network.webSocket" in network_log["method"]):
                f.write(dumps(network_log)+",") 
        f.write("{}]")
    driver.quit()
    json_file_path = "network_log.json"
    with open(json_file_path, "r", encoding="utf-8") as f: 
        logs = loads(f.read()) 

    print("Sorting the pages...")
    page_links = []
    for log in logs:
        try:
            url = log["params"]["request"]["url"] 
            if "files/large/" in url:
                page_links.append(url.split('?')[0])
        except Exception: pass

    if flips > 0: 
        for i in range(flips):
            p1 = 3 + 2 * i
            p2 = 4 + 2 * i
            if p2 < len(page_links):
                page_links[p1], page_links[p2] = page_links[p2], page_links[p1]

    images = []
    for page in range(len(page_links)):
        print("Loading pages " + str(page + 1) + "/" + str(NUM_PAGES) + "...", end="\r")
        images.append(Image.open(BytesIO(requests.get(page_links[page]).content)).convert("RGB"))

    print("\nSaving to PDF...")
    images[0].save("result-" + str(round(time() * 1000)) + ".pdf", save_all=True, append_images=images[1:])
    print("Done!")