#!/usr/bin/env python3
"""news-image-20261123 entry runner.

Copies the pre-rendered entry.png (23 November 2026 world news, drawn
with PIL shapes and text) into the make.fun output directory and
verifies the copy is byte-identical to the source.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path

SOURCE_NAME = "entry.png"
MAX_BYTES = 1_048_576  # make.fun cap: 1 MiB
MAX_DIMENSION = 1024  # make.fun cap: 1024x1024


def png_dimensions(path):
    """Read width/height from a PNG header without decoding pixels."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    width = int.from_bytes(header[16:20], "big")
    height = int.from_bytes(header[20:24], "big")
    return width, height


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    here = Path(__file__).resolve().parent
    source = here / SOURCE_NAME
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / SOURCE_NAME

    if not source.is_file():
        print(f"error: {source} not found", file=sys.stderr)
        return 1

    if source.stat().st_size > MAX_BYTES:
        print(f"error: {source} exceeds the {MAX_BYTES}-byte cap", file=sys.stderr)
        return 1
    width, height = png_dimensions(source)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        print(f"error: {source} is {width}x{height}, over the "
              f"{MAX_DIMENSION}x{MAX_DIMENSION} cap", file=sys.stderr)
        return 1

    shutil.copyfile(source, target)

    if sha256_of(source) != sha256_of(target):
        print("error: copy failed verification (hash mismatch)", file=sys.stderr)
        return 1

    size = target.stat().st_size
    print(f"wrote {target} ({width}x{height}, {size} bytes, sha256 verified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
