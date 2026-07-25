import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8501"
OUT = r"E:\新建文件夹\UL_Portfolio\ai_trust_layer\screenshots"


def wait_text(page, text, timeout=20000):
    start = time.time()
    while time.time() - start < timeout / 1000.0:
        try:
            body = page.evaluate("document.body ? document.body.innerText : ''")
            if text in body:
                return
        except Exception:
            pass
        time.sleep(0.4)
    raise TimeoutError(f"text not found within {timeout}ms: {text!r}")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 1500})

    page.goto(BASE, wait_until="domcontentloaded")
    wait_text(page, "Every AI answer")
    # Go to Admin
    page.get_by_role("button", name="Admin").click()
    wait_text(page, "TRUST LAYER ANALYTICS")
    time.sleep(2.5)  # let altair charts render
    page.screenshot(path=f"{OUT}/p1_admin_full.png", full_page=True)

    # Section-only screenshot of the charts region
    page.screenshot(path=f"{OUT}/p1_admin_charts.png", full_page=False)
    browser.close()
print("DONE")
