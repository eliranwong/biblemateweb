from nicegui import app, ui
from typing import Optional

# Define the API endpoint
# Note: NiceGUI exposes the underlying FastAPI instance via 'app'
@app.get('/api/ask')
def api_ask(query: str, token: Optional[str] = None):
    """
    Endpoint for BibleMate AI.
    - query: Required (automatically required because no default value is provided)
    - token: Optional (defaults to None)
    """
    
    # 1. Validate Token (Example logic)
    if token == "SECRET_Pass":
        auth_status = "Authorized"
    else:
        auth_status = "Public/Unauthorized"

    # 2. Process the query (Your BibleMate logic goes here)
    # For now, we just echo the data back
    result = {
        "received_query": query,
        "auth_status": auth_status,
        "token_used": token,
        "message": f"Processing bible query: '{query}'"
    }

    return result

# Simple UI to ensure the app runs
ui.label('BibleMate AI - API is running').classes('text-2xl m-4')
ui.label('Try visiting: /api/ask?query=Genesis&token=123').classes('m-4')

ui.run(port=9999, reload=False)