import requests

def check_debug():
    try:
        resp = requests.get("http://localhost:9222/json", timeout=2)
        print("Chrome Debug Port 9222 is OPEN.")
        print("Tabs:", len(resp.json()))
        found = False
        for tab in resp.json():
            if "notebooklm.google" in tab.get("url", ""):
                 print(f"Found NotebookLM Tab: {tab['url']}")
                 found = True
        if not found:
             print("NotebookLM Tab NOT found.")
    except Exception as e:
        print(f"Chrome Debug Port 9222 is CLOSED or not reachable. Error: {e}")

if __name__ == "__main__":
    check_debug()
