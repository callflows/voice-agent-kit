#!/usr/bin/env python3
"""
ElevenLabs ConvAI Knowledge Base — Create Text Document
Uploads a text document to the workspace knowledge base.

POST /v1/convai/knowledge-base/text  {name, text}  -> {id, name, folder_path}

Input is a text file. If the file contains the marker '## KB Content (Upload)'
(the vac-knowledge-base convention), ONLY the part after that marker is uploaded
(the meta block stays local). Otherwise the whole file is uploaded.
"""

import os
import re
import sys
import json
import urllib.request
import urllib.error

API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.eu.residency.elevenlabs.io")
API_KEY = os.environ.get("ELEVENLABS_API_KEY")
UPLOAD_MARKER = "## KB Content (Upload)"
# Strings that must NEVER appear in an uploaded payload — they mark local-only meta.
META_LEAK_MARKERS = (
    "## Meta",
    "do not upload",
    "Upload boundary",
    "Review flags",
    "Deploy handoff",
    "tier-1 Spec",
    "tier-1 spec",
    "Quality Gate",
)

if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)


def extract_payload(raw: str) -> str:
    """Return only the uploadable payload (after the marker HEADER, if present).

    The marker is matched ONLY as a standalone header line (start of line), so an
    in-prose mention of the marker string inside the meta block can never become
    the cut point (a real bug fixed 2026-06-22). A trailing local-only section
    (e.g. '## Deploy-Handoff', '## Quality Gate') after the content is dropped.
    """
    m = re.search(r'(?m)^%s\s*$' % re.escape(UPLOAD_MARKER), raw)
    if m is None:
        # No marker: upload the whole file, but still guard against meta leakage.
        payload = raw.strip() + "\n"
    else:
        payload = raw[m.end():]
        # Drop any trailing local-only section that follows the content.
        cut = re.search(r'(?m)^---\s*$\s*^## (Deploy-Handoff|Quality Gate)', payload)
        if cut:
            payload = payload[:cut.start()]
        payload = payload.strip() + "\n"
    leaked = [mk for mk in META_LEAK_MARKERS if mk in payload]
    if leaked:
        print(f"ERROR: meta content leaked into the upload payload: {leaked} — check markers", file=sys.stderr)
        sys.exit(1)
    return payload


def create_kb_text(name: str, text: str) -> dict:
    if len(text.encode("utf-8")) < 500:
        print("ERROR: payload < 500 bytes — too small to be RAG-indexed", file=sys.stderr)
        sys.exit(1)
    url = f"{API_BASE}/v1/convai/knowledge-base/text"
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    data = json.dumps({"name": name, "text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERROR: API returned {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 create_kb_text.py <name> <text_file>")
        print("  <text_file> may be a knowledge-base.md (only the '## KB Content (Upload)' part is sent)")
        sys.exit(1)

    name, text_file = sys.argv[1], sys.argv[2]
    if not os.path.exists(text_file):
        print(f"ERROR: Text file not found: {text_file}", file=sys.stderr)
        sys.exit(1)

    with open(text_file, "r", encoding="utf-8") as f:
        payload = extract_payload(f.read())

    result = create_kb_text(name, payload)
    print(json.dumps(result, indent=2, ensure_ascii=False))
