from utils.notebook_client import NotebookLMClient
import os
import json

def test_list():
    # check files
    user_home = os.path.expanduser("~")
    f1 = os.path.join(user_home, ".notebooklm-mcp", "auth.json")
    f2 = os.path.join(user_home, ".notebooklm-auth.json")
    
    print(f"Checking {f1}: {os.path.exists(f1)}")
    if os.path.exists(f1):
        with open(f1) as f:
            data = json.load(f)
            print(f"  Token extracted at: {data.get('extracted_at')}")

    print(f"Checking {f2}: {os.path.exists(f2)}")
    if os.path.exists(f2):
        with open(f2) as f:
            data = json.load(f)
            print(f"  Token extracted at: {data.get('extracted_at')}")
            
    print("\nAttempting to list notebooks...")
    client = NotebookLMClient()
    try:
        notebooks = client.list_notebooks()
        print(f"Result: {notebooks}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_list()
