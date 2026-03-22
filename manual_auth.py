import requests
import websocket
import json
import re
import time
import os
from pathlib import Path

# Constants
NOTEBOOKLM_URL = "https://notebooklm.google.com/"
CDP_PORT = 9222

def get_debugger_url():
    try:
        resp = requests.get(f"http://localhost:{CDP_PORT}/json", timeout=2)
        tabs = resp.json()
        for tab in tabs:
            if "notebooklm.google.com" in tab.get("url", ""):
                 print(f"Found NotebookLM tab: {tab['url']}")
                 return tab.get("webSocketDebuggerUrl")
        print("NotebookLM tab not found in open tabs.")
        return None
    except Exception as e:
        print(f"Error connecting to Chrome debugger: {e}")
        return None

def execute_cdp(ws_url, method, params={}):
    ws = websocket.create_connection(ws_url)
    try:
        msg = {"id": 1, "method": method, "params": params}
        ws.send(json.dumps(msg))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == 1:
                return resp.get("result", {})
    finally:
        ws.close()

def extract_tokens(ws_url):
    print("Extracting tokens...")
    
    # 1. Cookies
    cookies_res = execute_cdp(ws_url, "Network.getCookies", {"urls": [NOTEBOOKLM_URL]})
    cookies_list = cookies_res.get("cookies", [])
    cookies = {c["name"]: c["value"] for c in cookies_list}
    print(f"Found {len(cookies)} cookies.")
    
    # 2. Page Content (for CSRF/Session)
    html_res = execute_cdp(ws_url, "Runtime.evaluate", {"expression": "document.documentElement.outerHTML"})
    html = html_res.get("result", {}).get("value", "")
    
    # Extract CSRF
    csrf_token = ""
    # Patterns from auth.py
    patterns = [
        r'"SNlM0e":"([^"]+)"', 
        r'at=([^&"]+)',
        r'"FdrFJe":"([^"]+)"'
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            csrf_token = m.group(1)
            break
            
    # Extract Session ID
    session_id = ""
    patterns_sid = [
        r'"FdrFJe":"([^"]+)"',
        r'f\.sid=(\d+)'
    ]
    for p in patterns_sid:
        m = re.search(p, html)
        if m:
            session_id = m.group(1)
            break
            
    return {
        "cookies": cookies,
        "csrf_token": csrf_token,
        "session_id": session_id,
        "extracted_at": time.time()
    }

def save_tokens(tokens):
    home = Path.home()
    
    # Locations
    locs = [
        home / ".notebooklm-auth.json",
        home / ".notebooklm-mcp" / "auth.json"
    ]
    
    for path in locs:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(tokens, f, indent=2)
        print(f"Saved tokens to {path}")

def main():
    print("Starting Manual Auth Extraction...")
    ws_url = get_debugger_url()
    if not ws_url:
        print("Failed to find NotebookLM tab. Please open NotebookLM in Chrome.")
        return
        
    tokens = extract_tokens(ws_url)
    if not tokens["cookies"]:
        print("No cookies found!")
        return
        
    print(f"CSRF Token: {tokens['csrf_token']}")
    print(f"Session ID: {tokens['session_id']}")
    
    save_tokens(tokens)
    print("Authentication Refreshed Successfully!")

if __name__ == "__main__":
    main()
