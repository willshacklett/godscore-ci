#!/usr/bin/env python3
"""
api/verify_attestation.py

Verifies a GodScore attestation signed with HMAC-SHA256.

Usage:
  python api/verify_attestation.py <attestation.json> <hmac_secret>

Returns exit 0 if valid, exit 1 if invalid.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sys
from typing import Any, Dict


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def canonical_json_bytes(obj: Dict[str, Any]) -> bytes:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")


def hmac_sha256_b64(secret: str, payload: bytes) -> str:
    mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()
    return base64.b64encode(mac).decode("utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python api/verify_attestation.py <attestation.json> <hmac_secret>")
        return 1

    path = argv[1]
    secret = argv[2]

    a = load_json(path)

    sig = a.get("signature")
    if not isinstance(sig, dict):
        print("❌ No signature field present")
        return 1

    sig_val = sig.get("value", "")
    if not isinstance(sig_val, str) or not sig_val:
        print("❌ Signature value missing/empty")
        return 1

    # Remove signature for verification
    unsigned = dict(a)
    unsigned.pop("signature", None)

    expected = hmac_sha256_b64(secret, canonical_json_bytes(unsigned))

    if hmac.compare_digest(expected, sig_val):
        print("✅ Signature valid")
        return 0

    print("❌ Signature invalid")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
