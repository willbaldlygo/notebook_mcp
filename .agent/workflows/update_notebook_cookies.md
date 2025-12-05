---
description: Update authentication cookies for NotebookLM
---
# Update NotebookLM Cookies

1.  **Request Cookies**: Ask the user to provide their fresh cookies.
    *   *Instructions*: "Please log in to [NotebookLM](https://notebooklm.google.com/), open DevTools (F12) -> Application -> Cookies, and copy everything. Paste it here."

2.  **Save Cookies**:
    *   Run the update script with the provided content.
    *   Command: `python3 update_cookies.py "PASTED_CONTENT"` (Use single quotes if content has double quotes, or pass via stdin).

3.  **Verify**:
    *   Run a quick connection test to confirm it works.
