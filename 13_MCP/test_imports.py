# Test script to see what's available in langchain_mcp_adapters
try:
    import langchain_mcp_adapters
    print("✅ Successfully imported langchain_mcp_adapters")
    
    # Try to get version info
    try:
        print(f"Package version: {langchain_mcp_adapters.__version__}")
    except AttributeError:
        print("Package version: Not available via __version__")
    
    print("\n🔍 Available attributes:")
    for attr in dir(langchain_mcp_adapters):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    
    print("\n🔍 Looking for MCP-related classes:")
    for attr in dir(langchain_mcp_adapters):
        if 'mcp' in attr.lower() or 'tool' in attr.lower():
            print(f"  - {attr}")
            
    # Try to see what's in the package
    print("\n🔍 Package contents:")
    print(f"Package location: {langchain_mcp_adapters.__file__}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")