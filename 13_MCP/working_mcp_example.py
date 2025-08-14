#!/usr/bin/env python3
"""
Working MCP Integration Example

This demonstrates a complete, working integration of MCP tools with LangGraph.
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.sessions import StdioConnection

# Load environment variables
load_dotenv()

async def working_mcp_demo():
    """Complete working MCP integration demo"""
    print("🚀 Working MCP Integration Demo")
    print("=" * 50)
    
    # 1. Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # 2. Load MCP tools
    print("📥 Loading MCP tools...")
    connection = StdioConnection(
        command="uv",
        args=["--directory", "/Users/ludovicagonella/code/AIE7/13_MCP", "run", "server.py"],
        transport="stdio"
    )
    mcp_tools = await load_mcp_tools(None, connection=connection)
    
    print(f"✅ Loaded {len(mcp_tools)} tools:")
    for tool in mcp_tools:
        print(f"  - {tool.name}: {tool.description}")
    
    print("\n" + "=" * 50)
    
    # 3. Test different scenarios
    test_cases = [
        "Roll a d6 die for me",
        "Generate a password with 12 characters",
        "Roll 3 dice with notation 2d8"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_input}")
        print("-" * 40)
        
        # Bind tools with tool_choice="auto" (CRITICAL!)
        llm_with_tools = llm.bind_tools(mcp_tools, tool_choice="auto")
        
        # Get response from LLM
        response = llm_with_tools.invoke([HumanMessage(content=test_input)])
        
        print(f"🤖 AI Response: {response.content}")
        
        # Check for tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"🔧 Tools called: {len(response.tool_calls)}")
            
            # Execute each tool call ASYNCHRONOUSLY
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                print(f"  - Executing {tool_name} with args: {tool_args}")
                
                # Find and execute the tool ASYNCHRONOUSLY
                for tool in mcp_tools:
                    if tool.name == tool_name:
                        try:
                            # Use await for async tools
                            if asyncio.iscoroutinefunction(tool.ainvoke):
                                result = await tool.ainvoke(tool_args)
                            else:
                                result = await tool.ainvoke(tool_args)
                            
                            print(f"    ✅ Result: {result}")
                            
                            # Create tool message for follow-up
                            tool_message = ToolMessage(
                                content=str(result),
                                tool_call_id=tool_call.get('id', ''),
                                name=tool_name
                            )
                            
                            # Get follow-up response from LLM
                            follow_up_response = llm_with_tools.invoke([
                                HumanMessage(content=test_input),
                                response,
                                tool_message
                            ])
                            
                            print(f"🤖 Follow-up: {follow_up_response.content}")
                            
                        except Exception as e:
                            print(f"    ❌ Tool execution error: {e}")
                        break
        else:
            print("ℹ️  No tools were called")
        
        print("-" * 40)
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")

async def interactive_mode(mcp_tools, llm):
    """Interactive conversation mode"""
    print("\n💬 Interactive Mode - Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if user_input:
            print(f"\n🤖 Processing: {user_input}")
            print("-" * 30)
            
            # Bind tools with tool_choice="auto"
            llm_with_tools = llm.bind_tools(mcp_tools, tool_choice="auto")
            
            # Get response from LLM
            response = llm_with_tools.invoke([HumanMessage(content=user_input)])
            
            print(f"🤖 AI: {response.content}")
            
            # Execute tools if called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"🔧 Executing {len(response.tool_calls)} tool(s)...")
                
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    
                    print(f"  - {tool_name}({tool_args})")
                    
                    # Execute tool
                    for tool in mcp_tools:
                        if tool.name == tool_name:
                            try:
                                result = await tool.ainvoke(tool_args)
                                print(f"    ✅ Result: {result}")
                                
                                # Get follow-up
                                tool_message = ToolMessage(
                                    content=str(result),
                                    tool_call_id=tool_call.get('id', ''),
                                    name=tool_name
                                )
                                
                                follow_up = llm_with_tools.invoke([
                                    HumanMessage(content=user_input),
                                    response,
                                    tool_message
                                ])
                                
                                print(f"🤖 Follow-up: {follow_up.content}")
                                
                            except Exception as e:
                                print(f"    ❌ Error: {e}")
                            break
            else:
                print("ℹ️  No tools called")
            
            print("-" * 30)

async def main():
    """Main function"""
    try:
        # Run the demo
        await working_mcp_demo()
        
        # Ask if user wants interactive mode
        response = input("\n🎮 Would you like to try interactive mode? (y/n): ").strip().lower()
        
        if response in ['y', 'yes']:
            # Load tools again for interactive mode
            connection = StdioConnection(
                command="uv",
                args=["--directory", "/Users/ludovicagonella/code/AIE7/13_MCP", "run", "server.py"],
                transport="stdio"
            )
            mcp_tools = await load_mcp_tools(None, connection=connection)
            
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            await interactive_mode(mcp_tools, llm)
        
        print("\n👋 Thanks for trying the MCP integration!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 