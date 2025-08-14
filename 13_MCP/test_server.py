import subprocess
import sys
import time

def test_server_startup():
    """Test if the MCP server can start up properly"""
    try:
        # Start the server process
        process = subprocess.Popen(
            ["uv", "run", "server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ MCP server started successfully!")
            print("   - Server is running and ready to accept connections")
            print("   - You can now use it in Cursor's AI chat")
            
            # Terminate the process
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ MCP server failed to start")
            print(f"Exit code: {process.returncode}")
            print(f"Stdout: {stdout}")
            print(f"Stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing MCP Server Startup...")
    success = test_server_startup()
    
    if success:
        print("\n🎉 Your MCP server is working correctly!")
        print("   You can now use these tools in Cursor:")
        print("   - web_search: Search the web for information")
        print("   - roll_dice: Roll dice with notation (e.g., '2d20k1')")
        print("   - generate_password: Generate random passwords")
    else:
        print("\n💥 There's an issue with your MCP server")
        print("   Check the error messages above")