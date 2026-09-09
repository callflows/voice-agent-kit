#!/usr/bin/env python3
"""
ElevenLabs Voice Library Script
Lists available voices (requires voices_read permission).
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


def list_voices(language: str = None) -> dict:
    """
    List available voices.
    
    Args:
        language: Optional language filter (e.g., 'de')
        
    Returns:
        dict: API response with voices array
    """
    url = f"{API_BASE}/v1/voices"
    if language:
        url += f"?language={language}"
    
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
    language = sys.argv[1] if len(sys.argv) > 1 else None
    
    result = list_voices(language)
    
    # Pretty-print voices
    if "voices" in result:
        print(f"Found {len(result['voices'])} voices\n")
        for voice in result["voices"]:
            labels = voice.get("labels", {})
            print(f"{voice['voice_id']:<30} | {voice['name']:<25} | {labels.get('language', 'N/A')}")
    else:
        print(json.dumps(result, indent=2))
