#!/usr/bin/env python3
"""Meme Sprint 3 (burn) entrypoint: copy the shipped entry.png to the output.

The image itself is rendered by render.py (PIL + DejaVu Sans Mono, no network,
no model call) and committed to this repo; this program only copies it into
/output/entry.png and verifies its sha256, so the graded run is deterministic
and dependency-free.
"""
import hashlib
import os
import sys

EXPECTED_SHA256 = "5117e6b0649a830e874a6bc03fb61b83abb1c23b467a57100a2f92c8914733a3"


def check_gate(data):
    """Mirror the competition gate: whole PNG, <=1 MiB, <=1024x1024."""
    if len(data) > 1_048_576:
        return "over the 1 MiB gate: %d bytes" % len(data)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return "not a PNG"
    if len(data) < 33 or data[12:16] != b"IHDR":
        return "missing IHDR"
    w = int.from_bytes(data[16:20], "big")
    h = int.from_bytes(data[20:24], "big")
    if w > 1024 or h > 1024:
        return "over the 1024x1024 gate: %dx%d" % (w, h)
    return None


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(src, "rb") as f:
        data = f.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        print("entry.png sha256 mismatch: got " + digest, file=sys.stderr)
        return 1
    problem = check_gate(data)
    if problem:
        print("entry.png fails the gate: " + problem, file=sys.stderr)
        return 1
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as f:
        f.write(data)
    with open(out_path, "rb") as f:
        back = f.read()
    if hashlib.sha256(back).hexdigest() != digest:
        print("read-back sha256 mismatch", file=sys.stderr)
        return 1
    print("wrote entry.png (" + str(len(data)) + " bytes, sha256 " + digest + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
