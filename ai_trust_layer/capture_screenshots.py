"""
Screenshot capture script for AI Trust Layer demo.
Uses Playwright with system Chrome to capture screenshots per Step 6 demo script.

Scenes:
  1. Idle state (search page)
  2. High confidence (green label + details expanded)
  3. Low confidence (red alert banner + action link)
  4. Medium confidence (dual expander: sources open + jargon closed)
  5. Admin Dashboard (3 metrics + jargon table + recent queries)
"""

import time
import os
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
APP_URL = "http://localhost:8501"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def wait_for_streamlit(page, timeout=15):
    """Wait for Streamlit app to fully load."""
    page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=timeout * 1000)
    time.sleep(2)  # Extra wait for widgets to render


def take_screenshot(page, name, full_page=True):
    """Take a screenshot and save it."""
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    page.screenshot(path=path, full_page=full_page)
    print(f"  Saved: {name}.png")
    return path


def type_and_search(page, query):
    """Type a query in the search box and click Search."""
    # Find the text input
    input_el = page.query_selector('input[aria-label="Enter your question:"]')
    if not input_el:
        input_el = page.query_selector('input[data-testid="stTextInput"]')
    if not input_el:
        # Fallback: find any text input
        input_el = page.query_selector('input[type="text"]')

    if input_el:
        input_el.fill("")
        input_el.fill(query)
        time.sleep(0.5)

    # Click the Search button
    btn = page.query_selector('button[kind="primary"]')
    if not btn:
        btn = page.query_selector('button:has-text("Search")')

    if btn:
        btn.click()
        time.sleep(2)  # Wait for response to render


def main():
    with sync_playwright() as p:
        # Launch system Chrome
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--start-maximized", "--no-sandbox"]
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            color_scheme="dark",
        )

        page = context.new_page()
        page.goto(APP_URL, wait_until="networkidle")
        wait_for_streamlit(page)

        print("=== Scene 1: Idle State ===")
        take_screenshot(page, "scene1_idle")

        print("=== Scene 2: High Confidence ===")
        type_and_search(page, "What signaling system does Project XX use?")
        time.sleep(2)
        take_screenshot(page, "scene2_high_confidence")

        # Expand the Details expander
        details_btn = page.query_selector('summary:has-text("Details")')
        if details_btn:
            details_btn.click()
            time.sleep(1)
        take_screenshot(page, "scene2_high_details_expanded")

        # Expand Jargon Glossary inside details
        jargon_btn = page.query_selector('summary:has-text("Jargon Glossary")')
        if jargon_btn:
            jargon_btn.click()
            time.sleep(1)
        take_screenshot(page, "scene2_high_jargon_expanded")

        print("=== Scene 3: Low Confidence ===")
        type_and_search(page, "What is the construction budget for YY Line?")
        time.sleep(2)
        take_screenshot(page, "scene3_low_confidence")

        # Expand details to show action link
        details_btn = page.query_selector('summary:has-text("Details")')
        if details_btn:
            details_btn.click()
            time.sleep(1)
        take_screenshot(page, "scene3_low_details_expanded")

        print("=== Scene 4: Medium Confidence (Dual Expander) ===")
        type_and_search(page, "What are the technical parameters of ZDJ-200 switch machine?")
        time.sleep(2)
        take_screenshot(page, "scene4_medium_confidence")

        # Sources expander should be auto-expanded, expand jargon
        jargon_btn = page.query_selector('summary:has-text("Jargon Glossary")')
        if jargon_btn:
            jargon_btn.click()
            time.sleep(1)
        take_screenshot(page, "scene4_medium_jargon_expanded")

        # Expand a formal definition
        def_btn = page.query_selector('summary:has-text("Formal Definition")')
        if def_btn:
            def_btn.click()
            time.sleep(1)
        take_screenshot(page, "scene4_medium_definition_expanded")

        print("=== Scene 5: Admin Dashboard ===")
        # Click "Switch to Admin"
        admin_btn = page.query_selector('button:has-text("Switch to Admin")')
        if admin_btn:
            admin_btn.click()
            time.sleep(2)

        # Use a taller viewport for admin to ensure all rows are rendered
        page.set_viewport_size({"width": 1920, "height": 2000})
        time.sleep(1)
        # Scroll to top to ensure full page is captured
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        take_screenshot(page, "scene5_admin_dashboard")

        print("\n=== All screenshots captured ===")
        print(f"Saved to: {SCREENSHOTS_DIR}")

        # List all files
        for f in sorted(os.listdir(SCREENSHOTS_DIR)):
            if f.endswith(".png"):
                fpath = os.path.join(SCREENSHOTS_DIR, f)
                size = os.path.getsize(fpath) // 1024
                print(f"  {f} ({size} KB)")

        browser.close()


if __name__ == "__main__":
    main()
