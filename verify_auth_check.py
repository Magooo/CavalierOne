from utils.notebook_client import NotebookLMClient
import sys
import json

def verify_auth():
    print("Verifying NotebookLM Authentication...")
    try:
        client = NotebookLMClient()
        result = client.list_notebooks()
        print(f"DEBUG: Result type: {type(result)}")
        # print(f"DEBUG: Full result: {result}")
        
        if isinstance(result, dict) and "error" in result:
             print(f"Auth Failed: {result['error']}")
             return False
        
        if isinstance(result, dict) and result.get("status") == "success":
             print("Auth Successful!")
             return True
             
        # Catch-all
        print(result)
        return True

    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    if not verify_auth():
        sys.exit(1)
