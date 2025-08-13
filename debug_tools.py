#!/usr/bin/env python3
"""
Debug script to test tool calling functionality
"""

from dotenv import load_dotenv
load_dotenv()

from backend.activity_adventure_agent import ActivityAdventureAgent
import json

def test_tools():
    print("🔧 Testing Adventure Weather Agent tools...")
    
    # Create agent
    agent = ActivityAdventureAgent()
    
    # Print tools
    print("\n📋 Available tools:")
    for i, tool in enumerate(agent.TOOLS, 1):
        print(f"{i}. {tool['function']['name']}: {tool['function']['description']}")
    
    # Print function registry
    print("\n🔗 Function registry:")
    for name, func in agent.function_registry.items():
        print(f"- {name}: {func}")
    
    # Test simple call that should trigger weather API
    print("\n🧪 Testing with: 'What's the weather in Seattle?'")
    response = agent.chat("What's the weather in Seattle?", [])
    print(f"Response: {response}")
    
    # Test direct LLM client with function calling
    print("\n🧪 Testing direct LLM client function calling...")
    llm_response = agent.llm_client.chat_with_function_calling(
        user_prompt="What's the weather in Seattle?",
        system_prompt="You are a helpful assistant. Use the get_weather tool to get weather information.",
        tools=agent.TOOLS,
        function_registry=agent.function_registry,
        debug=True
    )
    print(f"Direct LLM Response: {llm_response}")

if __name__ == "__main__":
    test_tools()