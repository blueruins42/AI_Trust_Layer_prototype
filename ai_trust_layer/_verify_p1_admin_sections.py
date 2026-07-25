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
    page = browser.new_page(viewport={"width": 1280, "height": 2400})

    page.goto(BASE, wait_until="domcontentloaded")
    wait_text(page, "Every AI answer")
    # Go to Admin
    page.get_by_role("button", name="Admin").click()
    wait_text(page, "TRUST LAYER ANALYTICS")
    time.sleep(2.5)

    # Full page capture (tall viewport ensures everything is visible)
    page.screenshot(path=f"{OUT}/p1_admin_full.png", full_page=True)

    # Section-specific viewport captures for close inspection
    page.get_by_text("High / Medium / Low Distribution").scroll_into_view_if_needed()
    time.sleep(0.5)
    page.screenshot(path=f"{OUT}/p1_admin_confidence.png")

    page.get_by_text("Term Heat & Glossary Candidates").scroll_into_view_if_needed()
    time.sleep(0.5)
    page.screenshot(path=f"{OUT}/p1_admin_jargon.png")

    browser.close()
print("DONE")
