import json
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configuration
ARTIFACTS_DIR = Path("/Users/will/.gemini/antigravity/brain/6ac700d1-78b2-4ef1-81e7-d60101a71d0f")
COOKIES_FILE = ARTIFACTS_DIR / "notebooklm_cookies.json"
USER_DATA_DIR = ARTIFACTS_DIR / "chrome_profile_mcp"

# Selectors
INPUT_SELECTOR = "textarea.query-box-input"
RESPONSE_SELECTOR = ".to-user-container .message-text-content"
THINKING_SELECTOR = "div.thinking-message"

class NotebookLMSession:
    def __init__(self, headless=True, executable_path=None):
        self.headless = headless
        self.executable_path = executable_path
        self.playwright = None
        self.context = None
        self.page = None
        # self._check_cookies() # No longer strict requirement

    def start(self):
        """Starts the persistent browser session if not already running."""
        if self.page and not self.page.is_closed():
            return

        print("🚀 Starting NotebookLM Browser Session...")
        self.playwright = sync_playwright().start()
        
        launch_args = {
            "user_data_dir": USER_DATA_DIR,
            "headless": self.headless,
            "user_agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        if self.executable_path:
            launch_args["executable_path"] = self.executable_path
            launch_args["channel"] = None # executable_path and channel are mutually exclusive
        else:
            launch_args["channel"] = "chrome"

        self.context = self.playwright.chromium.launch_persistent_context(**launch_args)
        
        self._inject_cookies()
        self.page = self.context.new_page()
        print("✅ Browser Session Started.")

    def _inject_cookies(self):
        if not COOKIES_FILE.exists():
            print("ℹ️  No cookies file found. Relying on persistent profile.")
            return

        try:
            with open(COOKIES_FILE, 'r') as f:
                content = f.read()
                
            valid_cookies = self.parse_cookies(content)
            if valid_cookies:
                self.context.add_cookies(valid_cookies)
                print(f"DEBUG: Injected {len(valid_cookies)} cookies.")
                
        except Exception as e:
            print(f"⚠️ Warning: Cookie injection failed: {e}")

    @staticmethod
    def parse_cookies(content):
        """Parses raw text (JSON or TSV) into Playwright-compatible cookie list."""
        if "/*" in content: content = content.split("/*")[0] # strip comments
        
        cookies = []
        try:
            cookies = json.loads(content)
        except json.JSONDecodeError:
            # TSV Fallback
            lines = content.strip().split('\n')
            for line in lines:
                if not line.strip(): continue
                parts = line.split('\t')
                if len(parts) < 2: continue
                
                name = parts[0].strip()
                value = parts[1].strip()
                domain = parts[2].strip() if len(parts) > 2 else ".google.com"
                path = parts[3].strip() if len(parts) > 3 else "/"
                if not path: path = "/"
                if not domain: domain = ".google.com"
                if ("notebooklm.google.com" in domain or "google.com" in domain) and not domain.startswith("."):
                    domain = "." + domain
                    
                # Secure/SameSite logic
                secure = False
                if len(parts) > 7:
                    val = parts[7].strip().lower()
                    if val == '✓' or val == 'true': secure = True
                if name.startswith("__Secure-") or name.startswith("__Host-"): secure = True
                
                same_site = "Lax"
                if len(parts) > 8:
                    val = parts[8].strip()
                    if val in ["Strict", "Lax", "None"]: same_site = val
                if same_site == "None": secure = True

                if name and value:
                    cookies.append({
                        "name": name, "value": value, "domain": domain, 
                        "path": path, "secure": secure, "sameSite": same_site
                    })

        valid_cookies = []
        for c in cookies:
            if c.get("name") == "PASTE_YOUR_COOKIES_HERE": continue
            valid_cookies.append({
                "name": c["name"],
                "value": c["value"],
                "domain": c.get("domain", ".google.com"),
                "path": c.get("path", "/"),
                "secure": c.get("secure", True),
                "sameSite": c.get("sameSite", "Lax")
            })
        return valid_cookies

    @staticmethod
    def save_cookies(raw_text):
        """Validates and saves raw cookie text to the storage file."""
        # Validate first
        try:
            cookies = NotebookLMSession.parse_cookies(raw_text)
            if not cookies:
                return False, "No valid cookies found in text."
            
            # Save if valid
            # We save the *original* text to preserve format (JSON/TSV) if user prefers,
            # OR we could save the parsed JSON. Saving parsed JSON is safer/cleaner.
            with open(COOKIES_FILE, 'w') as f:
                json.dump(cookies, f, indent=2)
                
            return True, f"Successfully saved {len(cookies)} cookies."
        except Exception as e:
            return False, str(e)

    def query(self, url, question):
        """Navigates to the notebook (if needed) and asks a question."""
        self.start() # Ensure alive
        
        try:
            # Only navigate if we aren't already there to save time
            if self.page.url != url:
                print(f"🌐 Navigating to {url}...")
                self.page.goto(url, wait_until="domcontentloaded")
            
            # Wait for input
            self.page.wait_for_selector(INPUT_SELECTOR, timeout=20000)
            
            # Type question
            self.page.click(INPUT_SELECTOR)
            self.page.fill(INPUT_SELECTOR, question)
            time.sleep(0.5)
            self.page.keyboard.press("Enter")
            
            # Wait for response
            # 1. Wait for thinking to start (short timeout)
            try: self.page.wait_for_selector(THINKING_SELECTOR, timeout=5000)
            except: pass
            
            # 2. Wait for thinking to end (long timeout)
            self.page.wait_for_selector(THINKING_SELECTOR, state="hidden", timeout=60000)
            
            # 3. Get response
            time.sleep(1) # buffer for render
            responses = self.page.query_selector_all(RESPONSE_SELECTOR)
            if not responses:
                return "Error: No response found."
                
            return responses[-1].inner_text()

        except Exception as e:
            print(f"FAIL URL: {self.page.url}")
            self.page.screenshot(path=ARTIFACTS_DIR / "debug_mcp_fail.png")
            return f"Error querying notebook: {e} (Screenshot saved)"

    def close(self):
        if self.context: self.context.close()
        if self.playwright: self.playwright.stop()
