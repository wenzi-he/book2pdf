import tkinter as tk
from tkinter import messagebox
import threading

from io import BytesIO
from json import dumps, loads
from math import floor
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep, time
from PIL import Image
from selenium.webdriver.chrome.service import Service
import sys
import os

def get_driver_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "chromedriver.exe")
    return "chromedriver.exe"

def run_task():
    LINK = entry.get().strip()

    if not LINK:
        messagebox.showwarning("Warning", "Please enter a link")
        return

    status_label.config(text="🔍 Initializing...")

    try:
        # Fix URL
        if "yunzhan365.com/basic/" in LINK:
            status_label.config(text="🔧 Fixing link...")
            soup = BeautifulSoup(requests.get(LINK).text, "html.parser")
            book_info = soup.find("div", {"class": "book-info"})
            title = book_info.find("h1", {"class": "title"})
            LINK = title.find("a").get("href")

        # Selenium configuration
        status_label.config(text="🌐 Launching browser...")
        caps = DesiredCapabilities.CHROME
        caps["goog:loggingPrefs"] = {"performance": "ALL"}

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("--log-level=3")

        service = Service(get_driver_path())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(LINK)
        sleep(5)

        NUM_PAGES = driver.execute_script("return originTotalPageCount;")

        flips = floor((NUM_PAGES - 3) / 2)
        for i in range(flips):
            status_label.config(text=f"📄 Flipping page {i+1}/{flips}")
            driver.execute_script('nextPageFun("mouse wheel flip")')
            sleep(0.5)

        status_label.config(text="📡 Fetching logs...")
        logs = driver.get_log("performance")
        driver.quit()

        # Extract image links
        page_links = []
        for log in logs:
            try:
                msg = loads(log["message"])["message"]
                url = msg["params"]["request"]["url"]
                if "files/large/" in url:
                    page_links.append(url.split("?")[0])
            except:
                pass

        # Sort
        for i in range(flips):
            p1 = 3 + 2 * i
            p2 = 4 + 2 * i
            if p2 < len(page_links):
                page_links[p1], page_links[p2] = page_links[p2], page_links[p1]

        # Download images
        images = []
        for i, url in enumerate(page_links):
            status_label.config(text=f"⬇️ Downloading {i+1}/{len(page_links)}")
            img = Image.open(BytesIO(requests.get(url).content)).convert("RGB")
            images.append(img)

        # Save PDF
        status_label.config(text="📚 Generating PDF...")
        filename = f"result-{int(time()*1000)}.pdf"
        images[0].save(filename, save_all=True, append_images=images[1:])

        status_label.config(text=f"✅ Complete: {filename}")
        messagebox.showinfo("Success", f"PDF generated: {filename}")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="❌ Error occurred")


def start_thread():
    threading.Thread(target=run_task).start()


# GUI
root = tk.Tk()
root.title("YunZhan Books to PDF Tool")
root.geometry("450x220")

tk.Label(root, text="Please enter link:").pack(pady=10)

entry = tk.Entry(root, width=55)
entry.pack()

tk.Button(root, text="Start Generating PDF", command=start_thread).pack(pady=20)

status_label = tk.Label(root, text="Waiting for input...", fg="blue")
status_label.pack()

root.mainloop()