#!/usr/bin/env python3
"""
ElevenLabs ConvAI Knowledge Base — Compute RAG Index
Triggers (or reads) the RAG index for a KB document and polls until it succeeds.

POST /v1/convai/knowledge-base/{document_id}/rag-index  {model}
  -> {id, model, status, progress_percentage, ...}

The embedding model used here MUST match the agent's `prompt.rag.embedding_model`,
otherwise retrieval will not match at runtime.

Valid models: e5_mistral_7b_instruct (default), multilingual_e5_large_instruct,
qwen3_embedding_4b.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.eu.residency.elevenlabs.io")
API_KEY = os.environ.get("ELEVENLABS_API_KEY")
DEFAULT_MODEL = "e5_mistral_7b_instruct"
TERMINAL_BAD = {"failed", "rag_limit_exceeded", "document_too_small", "cannot_index_folder"}

if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)


def post_index(document_id: str, model: str) -> dict:
    url = f"{API_BASE}/v1/convai/knowledge-base/{document_id}/rag-index"
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    data = json.dumps({"model": model}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERROR: API returned {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def compute_rag_index(document_id: str, model: str, max_polls: int = 30) -> dict:
    res = post_index(document_id, model)
    status = res.get("status")
    for i in range(max_polls):
        if status == "succeeded":
            return res
        if status in TERMINAL_BAD:
            print(f"ERROR: rag-index terminal status: {status}", file=sys.stderr)
            sys.exit(1)
        time.sleep(3)
        res = post_index(document_id, model)
        status = res.get("status")
        print(f"  poll {i}: status={status} progress={res.get('progress_percentage')}",
              file=sys.stderr)
    print(f"ERROR: rag-index not succeeded after polling (last status: {status})", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 compute_rag_index.py <document_id> [model]")
        print(f"  model defaults to {DEFAULT_MODEL}; MUST match agent prompt.rag.embedding_model")
        sys.exit(1)

    document_id = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL

    result = compute_rag_index(document_id, model)
    print(json.dumps(result, indent=2, ensure_ascii=False))
