from mcp.server.fastmcp import FastMCP
from notebook_session import NotebookLMSession

# Initialize the MCP Server
mcp = FastMCP("NoteBook MCP")

# Initialize the global browser session
# We initialize it lazily (on first request) or on startup? 
# Let's instantiate the class, but actual browser launch happens on first use in .start()
session = NotebookLMSession(headless=True)

@mcp.tool()
def query_notebook(url: str, question: str) -> str:
    """
    Queries a specific Google NotebookLM notebook.
    
    Args:
        url: The full URL of the notebook (e.g. https://notebooklm.google.com/notebook/...)
        question: The question to ask the notebook.
        
    Returns:
        The response text from NotebookLM.
    """
    try:
        return session.query(url, question)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.resource("notebooklm://status")
def get_status() -> str:
    """Returns the current status of the browser session."""
    if session.page and not session.page.is_closed():
        return f"Active (URL: {session.page.url})"
    return "Standby (Browser not launched)"

if __name__ == "__main__":
    mcp.run()
