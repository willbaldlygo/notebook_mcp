#!/usr/bin/env python3
"""
NotebookLM Authentication Setup
Launches a visible Chrome window for the user to log in to NotebookLM.
Saves the authentication state (cookies/storage) to a file for future use.
"""

import time
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configuration
ARTIFACTS_DIR = Path("/Users/will/.gemini/antigravity/brain/6ac700d1-78b2-4ef1-81e7-d60101a71d0f")
AUTH_FILE = ARTIFACTS_DIR / "notebooklm_auth.json"
USER_DATA_DIR = ARTIFACTS_DIR / "chrome_profile"  # Persistent profile for the session

def setup_auth():
    print("🚀 Launching NotebookLM Login Window...")
    print("👉 Please log in to your Google Account in the browser window that opens.")
    print("👉 Once you see your Notebooks dashboard, come back here and press ENTER.")

    with sync_playwright() as p:
        # Launch persistent context to keep "Remember Me" sessions active
        # We use a persistent context so the user's login is saved to the disk profile
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",  # Attempt to use installed Chrome
            headless=False,    # Visible window
            viewport={"width": 1280, "height": 720}
        )
        
        page = context.new_page()
        
        try:
            page.goto("https://notebooklm.google.com/")
        except Exception as e:
            print(f"⚠️  Error navigating: {e}")
            print("You can manually navigate to https://notebooklm.google.com in the window.")

        # Wait for user confirmation
        input("\n🟢 Press ENTER here once you are successfully logged in and can see your notebooks... ")

        print("\n💾 Saving authentication state...")
        
        # Save storage state (cookies + local storage)
        context.storage_state(path=AUTH_FILE)
        
        print(f"✅ Authentication saved to: {AUTH_FILE}")
        print("You can now close the browser window.")
        
        context.close()

if __name__ == "__main__":
    # Ensure artifacts dir exists (it should)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    setup_auth()
