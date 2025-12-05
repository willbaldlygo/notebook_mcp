---
description: Query NotebookLM with automatic authentication checking and recovery
---
# Query NotebookLM (Smart Auth)

This workflow ensures your agent can query NotebookLM even if cookies have expired, by proactively checking auth and prompting for a refresh.

1.  **Check Authentication**:
    *   Command: `python3 notebooklm_client.py --check-auth`
    *   **IF Exit Code 0**: (Success) Proceed to Step 3.
    *   **IF Exit Code 1**: (Failure) Proceed to Step 2.

2.  **Refresh Authentication (If Check Failed)**:
    *   **Prompt User**: "Authentication has expired. Please log in to [NotebookLM](https://notebooklm.google.com/), open DevTools (F12) -> Application -> Cookies, copy everything, and paste it here."
    *   **Wait for Input**.
    *   **Update Cookies**: Run `python3 update_cookies.py "USER_INPUT"`
    *   **Verify Again**: Run `python3 notebooklm_client.py --check-auth` to confirm.

3.  **Execute Query**:
    *   **Ask**: "What is the Notebook URL you want to query?" (If not already known)
    *   **Ask**: "What is your question?" (If not already known)
    *   **Run**: `python3 notebooklm_client.py --url "NOTEBOOK_URL" --question "YOUR_QUESTION"`
