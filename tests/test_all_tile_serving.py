#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

TILES_ROOT = Path("web/tiles")
SCRIPT = Path("tests/test_tile_serving.py")

if not SCRIPT.is_file():
    print(f"❌ Missing script: {SCRIPT}")
    exit(1)

if not TILES_ROOT.is_dir():
    print(f"❌ Not a tiles directory: {TILES_ROOT}")
    exit(1)

tile_dirs = sorted([d for d in TILES_ROOT.iterdir() if d.is_dir() and d.name.startswith("tiles_")])

if not tile_dirs:
    print("⚠️ No tile directories found.")
    exit(0)

for tiles_path in tile_dirs:
    print(f"🧪 Testing served tiles from: {tiles_path}")
    result = subprocess.run(["python3", str(SCRIPT), str(tiles_path)])
    if result.returncode != 0:
        print(f"❌ Tile serving test failed for {tiles_path}")
    else:
        print(f"✅ Tile serving verified for {tiles_path}")
