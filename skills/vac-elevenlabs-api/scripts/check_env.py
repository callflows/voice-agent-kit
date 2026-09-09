#!/usr/bin/env python3
"""
ElevenLabs environment check

Checks whether ELEVENLABS_API_KEY is set and valid. Meant for anyone who wants
to know the environment is in place before the first step of a skill.

Important: the auth test runs against GET /v1/voices, NOT against /v1/user.
The workspace key does not carry the user_read scope, so /v1/user returns a
false 401 even though the key is valid (verified 2026-06-29).

Usage:
    python3 check_env.py

Exit 0 = all good. Exit 1 = key missing or invalid (the message says what to do).
"""

import os
import sys
import urllib.request
import urllib.error

API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.eu.residency.elevenlabs.io")

def fail(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)
    print("→ Create a key: ElevenLabs dashboard → Profile → API Keys (scope: Conversational AI).", file=sys.stderr)
    sys.exit(1)

api_key = os.environ.get("ELEVENLABS_API_KEY")
if not api_key:
    fail("ELEVENLABS_API_KEY is not set. Set it in the environment: export ELEVENLABS_API_KEY=... "
         "(or 'set -a && source .env && set +a' from the skill directory).")

req = urllib.request.Request(f"{API_BASE}/v1/voices", headers={"xi-api-key": api_key})
try:
    with urllib.request.urlopen(req, timeout=15) as response:
        if response.status == 200:
            print("[OK] ELEVENLABS_API_KEY is set and valid (auth test against /v1/voices: 200).")
            sys.exit(0)
        fail(f"Unexpected status {response.status} during the auth test.")
except urllib.error.HTTPError as e:
    if e.code == 401:
        fail("The API key that is set is invalid (401 on /v1/voices). "
             "Check that the key is valid and enabled for Conversational AI.")
    fail(f"API answers with {e.code} during the auth test.")
except urllib.error.URLError as e:
    fail(f"ElevenLabs API unreachable ({e.reason}). Check network/firewall.")
