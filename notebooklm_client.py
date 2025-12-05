#!/usr/bin/env python3
"""
NotebookLM Client
Queries a Google NotebookLM notebook using saved authentication.
"""

import argparse
import sys
import time
from notebook_session import NotebookLMSession

def main():
    parser = argparse.ArgumentParser(description="Query NotebookLM")
    parser.add_argument("--question", help="Question to ask (required unless checking auth)")
    parser.add_argument("--visible", action="store_true", help="Show browser window")
    parser.add_argument("--check-auth", action="store_true", help="Just check if authentication is valid")
    
    args = parser.parse_args()
    
    # Initialize session
    session = NotebookLMSession(headless=not args.visible)

    if args.check_auth:
        print("🔍 Checking authentication status...")
        # Try to access main page and see if we get redirected to login
        # We use a known notebook URL or just the dashboard
        # Dashboard is safer: https://notebooklm.google.com/
        session.start()
        try:
            session.page.goto("https://notebooklm.google.com/", wait_until="domcontentloaded")
            time.sleep(2) # brief wait for redirect
            if "accounts.google.com" in session.page.url:
                print("❌ Authentication Expired (Redirected onto login page)")
                sys.exit(1)
            else:
                 # Double check we are not on some generic landing page
                 content = session.page.content()
                 if "Sign in" in content or "Welcome to NotebookLM" in content:
                     # This might be the public landing page if not logged in
                     print("❌ Authentication Invalid (Public landing page)")
                     sys.exit(1)
                     
            print("✅ Authentication Verified")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Check Failed: {e}")
            sys.exit(1)
        finally:
            session.close()

    if not args.question:
        print("Error: --question is required unless --check-auth is used")
        sys.exit(1)
    
    print(f"💬 Asking: {args.question}")
    answer = session.query(args.url, args.question)
    
    if answer:
        print("\n" + "="*80)
        print("NotebookLM Answer:")
        print("="*80)
        print(answer)
        print("="*80)

if __name__ == "__main__":
    main()
