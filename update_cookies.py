#!/usr/bin/env python3
"""
Update Cookies Script
Saves user-provided cookies string (JSON or TSV) to the secure storage.
"""
import sys
import argparse
from notebook_session import NotebookLMSession

def main():
    parser = argparse.ArgumentParser(description="Update NotebookLM Cookies")
    parser.add_argument("cookies", nargs='?', help="Cookie string (if empty, reads from stdin)")
    args = parser.parse_args()

    content = args.cookies
    if not content:
        print("Paste your cookies and press Ctrl+D (EOF):")
        content = sys.stdin.read()

    if not content.strip():
        print("❌ Error: No content provided.")
        sys.exit(1)

    success, msg = NotebookLMSession.save_cookies(content)
    
    if success:
        print("\n✅ " + msg)
    else:
        print("\n❌ Error saving cookies: " + msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
