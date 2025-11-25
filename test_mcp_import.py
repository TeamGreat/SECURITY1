import sys
import os

os.environ['OPENWEATHER_API_KEY'] = 'db9400b013c436f589afe364013ac4b9'
os.environ['NEWSAPI_KEY'] = 'ad9694cc4efb45f29abee16da516c7e8'
os.environ['SERPAPI_KEY'] = '52d2017d6d1e8d6dcac1985051f25b73d44bb0b2ed2aa65f0ee1578ac74b3e4a'

# Add the current directory to path
sys.path.insert(0, os.getcwd())

print("Attempting import...")
try:
    # Delete any cached imports
    if 'MCP' in sys.modules:
        del sys.modules['MCP']
    if 'MCP.server' in sys.modules:
        del sys.modules['MCP.server']
    
    # Fresh import
    import MCP.server as server_module
    print(f"Module loaded: {server_module}")
    print(f"Module __file__: {server_module.__file__}")
    print(f"Module dir: {[x for x in dir(server_module) if not x.startswith('_')]}")
    
    if hasattr(server_module, 'mcp_server'):
        print("\nSUCCESS: mcp_server found!")
        mcp = server_module.mcp_server
        print(f"Available tools: {list(mcp.get_available_tools().keys())}")
    else:
        print("\nFAILED: mcp_server not found in module")
        print(f"Module contents (all): {dir(server_module)}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
