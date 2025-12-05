#!/usr/bin/env python3
"""
NotebookLM Client
Queries a Google NotebookLM notebook using saved authentication.
"""

import argparse
from notebook_session import NotebookLMSession

def main():
    parser = argparse.ArgumentParser(description="Query NotebookLM")
    parser.add_argument("--url", required=True, help="URL of the Notebook")
    parser.add_argument("--question", required=True, help="Question to ask")
    parser.add_argument("--visible", action="store_true", help="Show browser window")
    parser.add_argument("--exe", help="Path to browser executable")
    
    args = parser.parse_args()
    
    # Initialize session
    session = NotebookLMSession(headless=not args.visible, executable_path=args.exe)
    
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
