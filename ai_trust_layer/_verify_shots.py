import os
import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8501"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")


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
    page = browser.new_page(viewport={"width": 1280, "height": 1200})

    # HOME
    page.goto(BASE, wait_until="domcontentloaded")
    wait_text(page, "Every AI answer")
    time.sleep(1.2)
    page.screenshot(path=f"{OUT}/verify_home.png", full_page=True)

    # HIGH (chip)
    page.goto(BASE, wait_until="domcontentloaded")
    wait_text(page, "Every AI answer")
    page.get_by_role("button", name="What signaling system does Project XX use?").click()
    wait_text(page, "High Confidence")
    time.sleep(1.2)
    page.screenshot(path=f"{OUT}/verify_high.png", full_page=True)

    # MEDIUM (chip)
    page.goto(BASE, wait_until="domcontentloaded")
    wait_text(page, "Every AI answer")
    page.get_by_role("button", name="ZDJ-200 switch machine parameters").click()
    wait_text(page, "Partial Match")
    time.sleep(1.2)
    page.screenshot(path=f"{OUT}/verify_medium.png", full_page=True)

    # LOW (chip -> alert banner)
    page.goto(BASE, wait_until="domcontentloaded")
    wait_text(page, "Every AI answer")
    page.get_by_role("button", name="YY Line construction budget").click()
    wait_text(page, "Manual verification required")
    time.sleep(1.2)
    page.screenshot(path=f"{OUT}/verify_low.png", full_page=True)

    # ADMIN
    page.goto(BASE, wait_until="domcontentloaded")
    wait_text(page, "Every AI answer")
    page.get_by_role("button", name="Admin").click()
    wait_text(page, "TRUST LAYER ANALYTICS")
    time.sleep(1.2)
    page.screenshot(path=f"{OUT}/verify_admin.png", full_page=True)

    browser.close()
print("DONE")
