#!/usr/bin/env python3
"""
NotebookLM Client
Queries a Google NotebookLM notebook using saved authentication.
"""

import argparse
import json
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configuration
ARTIFACTS_DIR = Path("/Users/will/.gemini/antigravity/brain/6ac700d1-78b2-4ef1-81e7-d60101a71d0f")
COOKIES_FILE = ARTIFACTS_DIR / "notebooklm_cookies.json"
USER_DATA_DIR = ARTIFACTS_DIR / "chrome_profile"

# Selectors
INPUT_SELECTOR = "textarea.query-box-input"
RESPONSE_SELECTOR = ".to-user-container .message-text-content"
THINKING_SELECTOR = "div.thinking-message"

def query_notebook(notebook_url, question, headless=True):
    if not COOKIES_FILE.exists():
        print(f"❌ Error: Cookies file not found at {COOKIES_FILE}")
        sys.exit(1)

    print(f"💬 Asking: {question}")
    
    with sync_playwright() as p:
        # Launch persistent context
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",
            headless=headless,
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Inject manual cookies
        try:
            with open(COOKIES_FILE, 'r') as f:
                content = f.read()
                # strip comments if any (simple approach)
                if "/*" in content:
                    content = content.split("/*")[0]
                
                cookies = []
                try:
                    # Try JSON first
                    cookies = json.loads(content)
                except json.JSONDecodeError:
                    # Try parsing raw DevTools Copy-Paste (TSV)
                    lines = content.strip().split('\n')
                    print(f"  Parsng {len(lines)} lines of text data...")
                    for line in lines:
                        if not line.strip(): continue
                        parts = line.split('\t')
                        
                        # Basic validation: We need at least Name and Value
                        if len(parts) < 2:
                            continue
                            
                        name = parts[0].strip()
                        value = parts[1].strip()
                        domain = parts[2].strip() if len(parts) > 2 else ".google.com"
                        path = parts[3].strip() if len(parts) > 3 else "/"
                        
                        # Fix empty path
                        if not path: 
                            path = "/"
                        
                        # Fix empty domain
                        if not domain:
                            domain = ".google.com"

                        # Ensure domain starts with dot if it's a google domain (standardize)
                        if "notebooklm.google.com" in domain or "google.com" in domain:
                            if not domain.startswith("."):
                                domain = "." + domain

                        # Columns (typical Chrome DevTools):
                        # 0: Name, 1: Value, 2: Domain, 3: Path, 4: Expires, 5: Size, 6: HttpOnly, 7: Secure, 8: SameSite ...
                        
                        secure = False
                        if len(parts) > 7:
                            # Chrome uses '✓' or 'true' or empty
                            val = parts[7].strip().lower()
                            if val == '✓' or val == 'true':
                                secure = True
                        
                        # Enforce secure for __Secure- prefix
                        if name.startswith("__Secure-") or name.startswith("__Host-"):
                            secure = True

                        same_site = "Lax" # Default
                        if len(parts) > 8:
                            val = parts[8].strip()
                            if val in ["Strict", "Lax", "None"]:
                                same_site = val
                            elif val == "":
                                same_site = "Lax" # fallback

                        # If SameSite is None, Secure must be True
                        if same_site == "None":
                            secure = True

                        if name and value:
                            cookies.append({
                                "name": name,
                                "value": value,
                                "domain": domain,
                                "path": path,
                                "secure": secure,
                                "sameSite": same_site
                            })
                
                # Filter/Fix cookies for Playwright
                valid_cookies = []
                for c in cookies:
                    if c.get("name") == "PASTE_YOUR_COOKIES_HERE":
                        continue

                    # Playwright STRICTLY requires either url or domain/path.
                    cookie = {
                        "name": c["name"],
                        "value": c["value"],
                        "domain": c.get("domain", ".google.com"),
                        "path": c.get("path", "/"),
                        "secure": c.get("secure", True), # Default to True for Google
                        "sameSite": c.get("sameSite", "Lax")
                    }
                    valid_cookies.append(cookie)
                
                if not valid_cookies:
                    print("❌ Error: No valid cookies extracted.")
                    return None

                # print(f"  Debug loading {len(valid_cookies)} cookies.")
                context.add_cookies(valid_cookies)
                print(f"✅ Injected {len(valid_cookies)} cookies.")

        except Exception as e:
            print(f"⚠️ Warning: Could not inject cookies: {e}")
            return None

        page = context.new_page()
        
        try:
            print("🌐 Navigating to notebook...")
            page.goto(notebook_url, wait_until="domcontentloaded")
            
            # Wait for input box
            print("waiting for input box...")
            page.wait_for_selector(INPUT_SELECTOR, timeout=20000)
            
            # Type question
            print("Typing question...")
            page.click(INPUT_SELECTOR)
            page.fill(INPUT_SELECTOR, question)
            time.sleep(0.5)
            page.keyboard.press("Enter")
            
            # Wait for response
            print("Waiting for answer...")
            
            # 1. Wait for "thinking" to appear (optional, might happen too fast)
            try:
                page.wait_for_selector(THINKING_SELECTOR, timeout=3000)
            except:
                pass 
                
            # 2. Wait for "thinking" to DISAPPEAR (meaning it's done)
            try:
                page.wait_for_selector(THINKING_SELECTOR, state="hidden", timeout=60000)
            except:
                pass # If it timed out, we check if we have a response anyway
            
            # 3. Get the latest response
            # We wait a bit to ensure the text is fully rendered
            time.sleep(2)
            
            responses = page.query_selector_all(RESPONSE_SELECTOR)
            if not responses:
                print("❌ No response found.")
                # Capture screenshot for debugging
                page.screenshot(path="debug_error.png")
                return None
                
            latest_response = responses[-1].inner_text()
            return latest_response

        except Exception as e:
            print(f"❌ Error during query: {e}")
            page.screenshot(path="debug_exception.png")
            return None
        finally:
            context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query NotebookLM")
    parser.add_argument("--url", required=True, help="URL of the Notebook")
    parser.add_argument("--question", required=True, help="Question to ask")
    parser.add_argument("--visible", action="store_true", help="Show browser window")
    
    args = parser.parse_args()
    
    answer = query_notebook(args.url, args.question, headless=not args.visible)
    
    if answer:
        print("\n" + "="*80)
        print("NotebookLM Answer:")
        print("="*80)
        print(answer)
        print("="*80)
