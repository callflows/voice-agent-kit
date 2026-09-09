#!/usr/bin/env python3
"""
ElevenLabs ConvAI Agent Retrieval Script
Fetches agent configuration via API.
"""

import os
import sys
import json
import urllib.request
import urllib.error

API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.eu.residency.elevenlabs.io")
API_KEY = os.environ.get("ELEVENLABS_API_KEY")

if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)


def get_agent(agent_id: str) -> dict:
    """
    Retrieve agent configuration.
    
    Args:
        agent_id: ElevenLabs agent ID
        
    Returns:
        dict: Full agent configuration
    """
    url = f"{API_BASE}/v1/convai/agents/{agent_id}"
    headers = {"xi-api-key": API_KEY}
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"ERROR: API returned {e.code}", file=sys.stderr)
        print(e.read().decode('utf-8'), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 get_agent.py <agent_id>")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    result = get_agent(agent_id)
    print(json.dumps(result, indent=2))
