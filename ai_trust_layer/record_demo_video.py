"""
record_demo_video.py - Record 3-minute demo video per Step 6 script.
Uses Playwright with system Chrome to capture the full interaction flow as a video.
"""

import time
import os
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
VIDEO_DIR = os.path.join(os.path.dirname(__file__), "videos")
APP_URL = "http://localhost:8501"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


DEMO_SCRIPT = [
    # (delay_seconds, description)
    (2.0, "Intro: showing the problem statement and search interface"),
    (2.0, "Scene 1: Empty search interface, ready for user query"),
]


def wait_for_streamlit(page, timeout=15):
    page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=timeout * 1000)
    time.sleep(2)


def type_and_search(page, query, delay=0.05):
    """Type a query and click Search."""
    input_el = page.query_selector('input[aria-label="Enter your question:"]') or \
               page.query_selector('input[data-testid="stTextInput"]') or \
               page.query_selector('input[type="text"]')

    if input_el:
        input_el.fill("")
        input_el.fill(query)
        time.sleep(0.5)

    btn = page.query_selector('button[kind="primary"]') or page.query_selector('button:has-text("Search")')
    if btn:
        btn.click()
        time.sleep(2.5)


def click_expander(page, text, wait=1.5):
    """Click an expander by its summary text."""
    btn = page.query_selector(f'summary:has-text("{text}")')
    if btn:
        btn.click()
        time.sleep(wait)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--start-maximized", "--no-sandbox"]
        )

        context = browser.new_context(
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1920, "height": 1080},
            viewport={"width": 1920, "height": 1080},
            color_scheme="dark",
        )

        page = context.new_page()
        page.goto(APP_URL, wait_until="networkidle")
        wait_for_streamlit(page)

        # --- Scene 1: Idle State ---
        print("[0:00-0:15] Scene 1: Idle state")
        time.sleep(3)

        # --- Scene 2: High Confidence ---
        print("[0:15-0:45] Scene 2: High confidence query")
        type_and_search(page, "What signaling system does Project XX use?")
        time.sleep(2)

        # Expand Details
        click_expander(page, "Details")
        time.sleep(1.5)

        # Expand Jargon Glossary
        click_expander(page, "Jargon Glossary")
        time.sleep(1.5)

        # Expand Formal Definition
        click_expander(page, "Formal Definition")
        time.sleep(1.5)

        # --- Scene 3: Low Confidence ---
        print("[1:45-2:15] Scene 3: Low confidence alert")
        type_and_search(page, "What is the construction budget for YY Line?")
        time.sleep(2)

        # Expand Details
        click_expander(page, "Details")
        time.sleep(1.5)

        # --- Scene 4: Medium Confidence ---
        print("[2:15-2:45] Scene 4: Medium confidence dual expander")
        type_and_search(page, "What are the technical parameters of ZDJ-200 switch machine?")
        time.sleep(2)

        # Sources are auto-expanded for medium; expand Jargon Glossary
        click_expander(page, "Jargon Glossary")
        time.sleep(1.5)

        # --- Scene 5: Admin Dashboard ---
        print("[2:45-3:00] Scene 5: Admin Dashboard")
        admin_btn = page.query_selector('button:has-text("Switch to Admin")')
        if admin_btn:
            admin_btn.click()
            time.sleep(3)

        # Scroll down to show full Recent Queries table
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)

        # Close context to finalize video
        context.close()
        browser.close()

        # Find generated video file and rename
        video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".webm")]
        if video_files:
            src = os.path.join(VIDEO_DIR, video_files[0])
            dst = os.path.join(VIDEO_DIR, "ai_trust_layer_demo.webm")
            os.rename(src, dst)
            size = os.path.getsize(dst) // 1024
            print(f"\n=== Demo video saved: {dst} ({size} KB) ===")
        else:
            print("\nNo video file found")


if __name__ == "__main__":
    main()
