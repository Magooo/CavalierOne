from utils.notebook_client import NotebookLMClient

# Mock methods to avoid subprocess call failing if setup is incomplete
def mock_call_tool(self, name, args):
    print(f"MOCK CALL > Tool: {name} | Args: {args}")
    if name == "notebook_list":
        return {"content": [{"type": "text", "text": '[{"id": "nb-1", "title": "Mock Notebook"}]'}]}
    if name == "notebook_create":
        return {"content": [{"type": "text", "text": '{"notebook_id": "nb-new-123", "title": "New Notebook"}'}]}
    return {"content": [{"type": "text", "text": "Mock Response"}]}

NotebookLMClient.call_tool = mock_call_tool

def test_notebook():
    print("Testing NotebookLM Client (Mocked)...")
    client = NotebookLMClient()
    
    print("Listing Notebooks...")
    print(client.list_notebooks())
    
    print("Creating Notebook...")
    print(client.create_notebook("Test Project"))

if __name__ == "__main__":
    test_notebook()
