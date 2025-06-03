#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

TILES_ROOT = Path("/home/jsbien/work/jsbien_glyph-miner/web_from_container/tiles")
SCRIPT = Path("tests/reconstruct_from_tiles.py")

if not SCRIPT.is_file():
    print(f"❌ Missing script: {SCRIPT}")
    exit(1)

if not TILES_ROOT.is_dir():
    print(f"❌ Not a tiles directory: {TILES_ROOT}")
    exit(1)

# tile_dirs = sorted([d for d in TILES_ROOT.iterdir() if d.is_dir() and d.name.startswith("tiles_")])
tile_dirs = sorted([d for d in TILES_ROOT.iterdir() if d.is_dir()])

if not tile_dirs:
    print("⚠️ No tile directories found.")
    exit(0)

for tiles_path in tile_dirs:
    print(f"🔄 Reconstructing from: {tiles_path}")
    result = subprocess.run(["python3", str(SCRIPT), str(tiles_path)])
    if result.returncode != 0:
        print(f"❌ Failed for {tiles_path}")
    else:
        print(f"✅ Done for {tiles_path}")
