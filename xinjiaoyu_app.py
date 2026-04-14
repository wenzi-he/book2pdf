import requests
from PIL import Image
from io import BytesIO
from time import time
import tkinter as tk
from tkinter import messagebox
import threading

# ================= Original Functions =================

def find_valid_pattern(base):
    patterns = [
        "files/assets/basic-html/page{}.jpg",
        "files/assets/basic-html/page{}.png",
        "files/assets/images/page{}.jpg",
        "files/assets/images/page{}.png",
        "files/mobile/{}.jpg",
        "files/mobile/{}.png",
        "files/pages/{}.jpg",
        "files/pages/{}.png",
    ]

    for pattern in patterns:
        test_url = base + pattern.format(1)
        try:
            r = requests.get(test_url)
            if r.status_code == 200:
                return pattern
        except:
            continue

    return None


def collect_images(base, pattern, max_pages=500):
    urls = []

    for i in range(1, max_pages + 1):
        url = base + pattern.format(i)
        r = requests.get(url)

        if r.status_code != 200:
            break

        urls.append(url)

    return urls


def download_images(urls):
    images = []

    for url in urls:
        try:
            content = requests.get(url).content
            img = Image.open(BytesIO(content)).convert("RGB")
            images.append(img)
        except:
            pass

    return images


def save_pdf(images):
    if not images:
        return None

    filename = f"result-{int(time()*1000)}.pdf"
    images[0].save(filename, save_all=True, append_images=images[1:])
    return filename


# ================= GUI =================

def run_task():
    url = entry.get().strip()

    if not url:
        messagebox.showwarning("Warning", "Please enter a link")
        return

    status_label.config(text="🔍 Processing...")

    try:
        base = url.replace("mobile/index.html", "")

        pattern = find_valid_pattern(base)
        if not pattern:
            status_label.config(text="❌ Image path not found")
            return

        status_label.config(text="📄 Collecting...")
        urls = collect_images(base, pattern)

        status_label.config(text="⬇️ Downloading...")
        images = download_images(urls)

        status_label.config(text="📚 Generating PDF...")
        pdf = save_pdf(images)

        if pdf:
            status_label.config(text=f"✅ Complete: {pdf}")
            messagebox.showinfo("Success", f"PDF generated: {pdf}")
        else:
            status_label.config(text="❌ Generation failed")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="❌ Error occurred")


def start_thread():
    t = threading.Thread(target=run_task)
    t.start()


# ================= Interface =================

root = tk.Tk()
root.title("XinJiaoYu Books to PDF Tool")
root.geometry("420x220")

tk.Label(root, text="Please enter link:").pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack()

tk.Button(root, text="Start Generating PDF", command=start_thread).pack(pady=20)

status_label = tk.Label(root, text="Waiting for input...", fg="blue")
status_label.pack()

root.mainloop()