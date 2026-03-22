import subprocess
import json
import threading
import time

def read_stream(stream, prefix):
    for line in iter(stream.readline, ''):
        print(f"[{prefix}] {line.strip()}")
        
def debug_mcp():
    cmd = "C:/Users/jason.m.chgv/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/Scripts/notebooklm-mcp.exe"
    
    print(f"Starting MCP: {cmd}")
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Start reader threads
    t1 = threading.Thread(target=read_stream, args=(process.stdout, "STDOUT"))
    t2 = threading.Thread(target=read_stream, args=(process.stderr, "STDERR"))
    t1.start()
    t2.start()
    
    # Send Initialize
    init_req = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "debug-client", "version": "1.0"}
        },
        "id": 1
    }
    print("Sending Initialize...")
    process.stdin.write(json.dumps(init_req) + "\n")
    process.stdin.flush()
    
    time.sleep(2)
    
    # Send List Notebooks
    list_req = {
        "jsonrpc": "2.0",
        "method": "notebooks/list", # Or whatever tool name is mapped? Wait, MCP uses tools/call usually.
        # But this server might support direct methods or specific tools.
        # The client uses tools/call with name="notebook_list"
        # Let's try tools/call
        "method": "tools/call",
        "params": {
            "name": "notebook_list",
            "arguments": {"max_results": 5}
        },
        "id": 2
    }
    
    print("Sending List Notebooks...")
    process.stdin.write(json.dumps(list_req) + "\n")
    process.stdin.flush()
    
    time.sleep(5)
    print("Closing...")
    process.terminate()

if __name__ == "__main__":
    debug_mcp()
