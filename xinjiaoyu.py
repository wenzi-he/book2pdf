import requests
from PIL import Image
from io import BytesIO
from time import time

def find_valid_pattern(base):
    print("🔍 正在探测图片路径...")

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
                print(f"✅ 找到路径: {pattern}")
                return pattern
        except:
            continue

    return None


def collect_images(base, pattern, max_pages=500):
    print("📄 正在收集图片...")
    urls = []

    for i in range(1, max_pages + 1):
        url = base + pattern.format(i)
        r = requests.get(url)

        if r.status_code != 200:
            break

        urls.append(url)
        print(f"找到第 {i} 页", end="\r")

    print(f"\n📄 共 {len(urls)} 页")
    return urls


def download_images(urls):
    images = []

    for i, url in enumerate(urls):
        try:
            print(f"⬇️ 下载 {i+1}/{len(urls)}", end="\r")
            content = requests.get(url).content
            img = Image.open(BytesIO(content)).convert("RGB")
            images.append(img)
        except:
            print(f"\n⚠️ 跳过 {url}")

    print("\n✅ 下载完成")
    return images


def save_pdf(images):
    if not images:
        print("❌ 没有图片")
        return

    filename = f"result-{int(time()*1000)}.pdf"
    images[0].save(filename, save_all=True, append_images=images[1:])
    print(f"📚 PDF 已生成: {filename}")


if __name__ == "__main__":
    url = input("📎 输入链接: ").strip()
    base = url.replace("mobile/index.html", "")

    pattern = find_valid_pattern(base)

    if not pattern:
        print("❌ 没找到图片路径（这个站结构特殊）")
        exit()

    urls = collect_images(base, pattern)
    images = download_images(urls)
    save_pdf(images)