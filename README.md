# NoteBook MCP

An **MCP (Model Context Protocol)** server that enables AI agents (like Claude Desktop) to query your personal **Google NotebookLM** notebooks.

It uses a persistent, local browser session (via Playwright) to bypass the lack of an official API, allowing for "warm start" instant queries.

## ✨ Features
*   **Zero-API Access**: Works with any Google account; no enterprise API required.
*   **Automatic Auth**: Reads cookies directly from your Chrome browser — no manual export needed.
*   **Warm Start**: Keeps a browser instance open in the background, making queries instant (after the first load).
*   **MCP Compliant**: Works out-of-the-box with any MCP client.

## 🚀 Setup

### 1. Installation
Clone this repository and install dependencies:

```bash
git clone https://github.com/your-username/notebook-mcp.git
cd notebook-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Authentication

#### Automatic (Recommended)
The tool automatically reads cookies from your Chrome browser:

1.  Log in to [NotebookLM](https://notebooklm.google.com/) in your regular Chrome browser.
2.  **Close Chrome** (required to read the cookie database).
3.  Run the MCP server — cookies are extracted automatically!

> **macOS Users**: On first run, you may be prompted to allow Keychain access. Click "Allow" to grant permission.

#### Manual Fallback
If automatic cookie reading fails (e.g., Chrome is open), you can still use manual export:

1.  Log in to [NotebookLM](https://notebooklm.google.com/) in Chrome.
2.  Open **DevTools** (Right-click -> Inspect) -> **Application** -> **Cookies**.
3.  Select `https://notebooklm.google.com`.
4.  Select all cookies (Cmd/Ctrl+A) and Copy (Cmd/Ctrl+C).
5.  Run: `python3 update_cookies.py "PASTE_HERE"`

> **Note**: Your `notebooklm_cookies.json` is git-ignored by default. Never commit it!

## 💻 Usage

### As an MCP Server (Claude Desktop)
Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "/absolute/path/to/notebook-mcp/.venv/bin/python3",
      "args": ["/absolute/path/to/notebook-mcp/server.py"]
    }
  }
}
```

### As a Library
You can use the session manager in your own Python scripts:

```python
from notebook_session import NotebookLMSession

session = NotebookLMSession(headless=True)
answer = session.query("https://notebooklm.google.com/notebook/...", "Summarize this doc")
print(answer)
```

## ⚠️ Limitations
*   **Session Expiry**: Google cookies expire every few weeks. If the tool stops working, log back into Chrome and restart.
*   **Chrome Must Be Closed**: For automatic cookie reading, Chrome must be closed (database is locked while running).
*   **Single Threaded**: The browser automation is not designed for high-concurrency requests.

## License
MIT
