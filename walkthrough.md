# NotebookLM Connection Walkthrough

We have successfully established a connection to your Google NotebookLM account using a local Python script powered by Playwright and your manually exported cookies.

## How it Works
1.  **Engine**: `notebooklm_client.py` uses Playwright to launch a headless browser.
2.  **Auth**: It injects the cookies you provided in `notebooklm_cookies.json`.
3.  **Action**: It navigates to the specified Notebook URL, types your question, and waits for the answer.

## Usage
To query your notebook, run the following command from the artifacts directory:

```bash
.venv/bin/python3 notebooklm_client.py --url "YOUR_NOTEBOOK_URL" --question "YOUR QUESTION"
```

### Example
```bash
.venv/bin/python3 notebooklm_client.py \
  --url "https://notebooklm.google.com/notebook/81d0a5ec-45df-4fcc-980b-f7ecf391a352" \
  --question "What are the core components of an AI agent?"
```

## NoteBook MCP Server
To run the persistent MCP server (which keeps the browser open for faster queries):

```bash
# Start the server (stdio)
.venv/bin/python3 server.py
```

### Features
*   **Warm Start**: The browser stays open in the background.
*   **Tools**: `query_notebook(url, question)`
*   **Resources**: `notebooklm://status` (Check browser state)

### Setup in Claude Desktop
To add this to Claude Desktop, add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "/Users/will/.gemini/antigravity/brain/6ac700d1-78b2-4ef1-81e7-d60101a71d0f/.venv/bin/python3",
      "args": ["/Users/will/.gemini/antigravity/brain/6ac700d1-78b2-4ef1-81e7-d60101a71d0f/server.py"]
    }
  }
}
```

## Maintenance
If the script stops working (e.g., returns "Login required" or fails to navigate), your session cookies may have expired.
1.  Log in to NotebookLM in Chrome.
2.  Export cookies again.
3.  Paste them into `notebooklm_cookies.json`.
