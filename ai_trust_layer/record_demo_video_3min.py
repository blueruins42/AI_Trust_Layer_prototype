"""
record_demo_video_3min.py - Record a ~3-minute demo video per Step 6 script.
Uses Playwright with system Chrome to capture the full interaction flow as a video.

Scene timings (approximate, matching Step 6 Demo Script):
  Scene 1: 0:00-0:15   Idle state / intro
  Scene 2: 0:15-1:00   High confidence + expand details + jargon
  Scene 3: 1:00-1:35   Low confidence alert + expand details
  Scene 4: 1:35-2:05   Medium confidence + dual expander
  Scene 5: 2:05-2:40   Admin Dashboard
  Scene 6: 2:40-3:00   Closing / back to frontend
"""

import time
import os
from playwright.sync_api import sync_playwright

VIDEO_DIR = os.path.join(os.path.dirname(__file__), "videos")
APP_URL = "http://localhost:8501"

os.makedirs(VIDEO_DIR, exist_ok=True)


def wait_for_streamlit(page, timeout=15):
    page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=timeout * 1000)
    time.sleep(2)


def type_and_search(page, query):
    """Type a query and click Search, then wait for response."""
    input_el = page.query_selector('input[aria-label="Enter your question:"]') or \
               page.query_selector('input[data-testid="stTextInput"]') or \
               page.query_selector('input[type="text"]')

    if input_el:
        input_el.fill("")
        input_el.fill(query)

    btn = page.query_selector('button[kind="primary"]') or page.query_selector('button:has-text("Search")')
    if btn:
        btn.click()
        time.sleep(3)


def click_expander(page, text):
    """Click an expander by its summary text."""
    btn = page.query_selector(f'summary:has-text("{text}")')
    if btn:
        btn.click()
        time.sleep(0.5)


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

        # --- Scene 1: Idle State (0:00-0:15) ---
        print("[0:00-0:15] Scene 1: Idle state")
        time.sleep(15)

        # --- Scene 2: High Confidence (0:15-1:00) ---
        print("[0:15-1:00] Scene 2: High confidence query")
        type_and_search(page, "What signaling system does Project XX use?")
        time.sleep(5)

        click_expander(page, "Details")
        time.sleep(5)

        click_expander(page, "Jargon Glossary")
        time.sleep(5)

        click_expander(page, "Formal Definition")
        time.sleep(10)

        # --- Scene 3: Low Confidence (1:00-1:35) ---
        print("[1:00-1:35] Scene 3: Low confidence alert")
        type_and_search(page, "What is the construction budget for YY Line?")
        time.sleep(8)

        click_expander(page, "Details")
        time.sleep(15)

        # --- Scene 4: Medium Confidence (1:35-2:05) ---
        print("[1:35-2:05] Scene 4: Medium confidence dual expander")
        type_and_search(page, "What are the technical parameters of ZDJ-200 switch machine?")
        time.sleep(5)

        # Sources are auto-expanded for medium; expand Jargon Glossary
        click_expander(page, "Jargon Glossary")
        time.sleep(8)

        click_expander(page, "Formal Definition")
        time.sleep(12)

        # --- Scene 5: Admin Dashboard (2:05-2:40) ---
        print("[2:05-2:40] Scene 5: Admin Dashboard")
        admin_btn = page.query_selector('button:has-text("Switch to Admin")')
        if admin_btn:
            admin_btn.click()
            time.sleep(5)

        # Scroll down to show full Recent Queries table
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(15)

        # --- Scene 6: Closing (2:40-3:00) ---
        print("[2:40-3:00] Scene 6: Closing")
        front_btn = page.query_selector('button:has-text("Switch to Frontend")')
        if front_btn:
            front_btn.click()
            time.sleep(10)

        # Close context to finalize video
        context.close()
        browser.close()

        # Rename generated video
        video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".webm")]
        for f in video_files:
            if f.startswith("ai_trust_layer_demo_3min"):
                continue
            src = os.path.join(VIDEO_DIR, f)
            dst = os.path.join(VIDEO_DIR, "ai_trust_layer_demo_3min.webm")
            os.replace(src, dst)  # overwrites if dst already exists
            size = os.path.getsize(dst) // 1024
            print(f"\n=== 3-min demo video saved: {dst} ({size} KB) ===")


if __name__ == "__main__":
    main()
