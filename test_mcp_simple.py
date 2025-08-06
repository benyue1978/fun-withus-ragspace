#!/usr/bin/env python3
"""
Simple MCP Tools Test
"""

import requests
import json

def test_mcp_tools():
    """Test MCP tools via HTTP API"""
    
    base_url = "http://localhost:8000"
    
    # Test list_docset
    print("Testing list_docset...")
    try:
        response = requests.post(
            f"{base_url}/api/list_docset/",
            json={},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test ask
    print("\nTesting ask...")
    try:
        response = requests.post(
            f"{base_url}/api/ask/",
            json={"query": "test", "docset": None},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mcp_tools() 