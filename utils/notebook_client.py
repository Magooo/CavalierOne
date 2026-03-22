import os
import json
import subprocess
import threading
from config import Config

class NotebookLMClient:
    def __init__(self):
        self.command = Config.NOTEBOOKLM_MCP_COMMAND
        self._lock = threading.Lock()



    # --- SIMPLIFIED APPROACH (Mocking/Placeholder for actual MCP impl) ---
    # Since writing a full async MCP client in a sync Flask view is tricky,
    # we will implement the critical logic using `subprocess` to call the `mcp-cli` 
    # OR we will just shell out to the `notebooklm-mcp-server` if it has CLI args.
    
    # ACTUALLY: The `notebooklm-mcp-server` IS the tool we installed.
    # It likely doesn't have a generic "run tool X" CLI flag. 
    # We probably need to interact with it via Stdio.
    
    # Let's write a helper to send a JSON-RPC request to the server process.

    def call_tool(self, name, args):
        """
        Connects to the MCP server process, sends a request, and returns result.
        """
        with self._lock:
            # Start process
            # Note: We need to know HOW to run it. 
            # If installed via pip: 'python -m notebooklm_mcp_server'
            # If uvx: 'uvx notebooklm-mcp-server'
            cmd_parts = self.command.split()
            
            try:
                process = subprocess.Popen(
                    cmd_parts,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8' # Ensure UTF-8 for JSON
                )
            except FileNotFoundError:
                return {"error": f"Command '{self.command}' not found."}

            # 1. Initialize (MCP Handshake)
            init_req = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0", # Adjust based on spec
                    "capabilities": {},
                    "clientInfo": {"name": "CavalierOne", "version": "1.0"}
                }
            }
            
            # 2. Call Tool
            tool_req = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": name,
                    "arguments": args
                }
            }

            try:
                # Send Init
                # process.stdin.write(json.dumps(init_req) + "\n")
                # process.stdin.flush()
                # # Read Init Response (Non-blocking read is hard with Popen, so this is fragile)
                # # Practical Shortcut: The server usually waits for input.
                
                # REVISION: Implementing a robust stdio JSON-RPC client from scratch here is risky 
                # given the timeout/blocking nature.
                # 
                # ALTERNATIVE: Attempt to use the `mcp` python package if available, 
                # but currently we are in a bit of a "custom integration" territory.
                #
                # SAFE FALLBACK: We will assume there is a `notebooklm-cli` or similar 
                # provided by the user, OR we assume we can control it via a wrapper.
                
                # Let's try to just write to it and read response.
                
                # Send Handshake
                process.stdin.write(json.dumps(init_req) + "\n")
                process.stdin.flush()
                
                # Read Init Response
                # We iterate lines until we get a response with id 1
                while True:
                    line = process.stdout.readline()
                    if not line: break
                    try:
                        resp = json.loads(line)
                        if resp.get("id") == 1:
                            break
                    except: pass
                
                # Submit 'notifications/initialized'
                process.stdin.write(json.dumps({
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }) + "\n")
                process.stdin.flush()

                # Send Tool Call
                process.stdin.write(json.dumps(tool_req) + "\n")
                process.stdin.flush()
                
                # Read Tool Response
                result = None
                while True:
                    line = process.stdout.readline()
                    if not line: break
                    try:
                        resp = json.loads(line)
                        if resp.get("id") == 2:
                            result = resp
                            break
                    except: pass
                
                process.terminate()
                
                if result and 'result' in result:
                    return result['result']
                elif result and 'error' in result:
                    return {"error": result['error']}
                return {"error": "No response from MCP server"}

            except Exception as e:
                process.kill()
                return {"error": str(e)}

    # -- Public API Methods --

    def list_notebooks(self):
        # Tool: notebook_list
        resp = self.call_tool("notebook_list", {"max_results": 20})
        # Parse output; MCP returns content list
        return self._parse_content(resp)

    def create_notebook(self, title):
        return self.call_tool("notebook_create", {"title": title})

    def add_url_source(self, notebook_id, url):
        return self.call_tool("notebook_add_url", {"notebook_id": notebook_id, "url": url})
    
    def add_text_source(self, notebook_id, text, title):
         return self.call_tool("notebook_add_text", {"notebook_id": notebook_id, "text": text, "title": title})

    def query(self, notebook_id, question):
        return self._parse_content(self.call_tool("notebook_query", {"notebook_id": notebook_id, "query": question}))

    def generate_audio(self, notebook_id):
        # Audio generation often requires "confirm=True"
        return self.call_tool("audio_overview_create", {"notebook_id": notebook_id, "confirm": True})

    def _parse_content(self, resp):
        # Helper to extract text from MCP response structure
        if not resp or "content" not in resp:
            return resp
        
        # Typically resp['content'] is a list of TextContent objects
        # [{"type": "text", "text": "..."}]
        final_text = ""
        for item in resp['content']:
            if item.get('type') == 'text':
                final_text += item.get('text', '')
        
        # Start a bit of cleanup if it's JSON stringified
        try:
            return json.loads(final_text)
        except:
            return final_text
