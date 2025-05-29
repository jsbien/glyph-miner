#!/usr/bin/env python3
import os
import sys
import requests
from pathlib import Path

def test_serving(tiles_dir):
    base_url = "http://localhost:9090/tiles"
    failed = 0
    total = 0

    print(f"🔍 Checking tiles served for: {tiles_dir}")
    for zoom in sorted(os.listdir(tiles_dir)):
        zoom_path = tiles_dir / zoom
        if not zoom_path.is_dir() or not zoom.isdigit():
            continue

        for x in sorted(os.listdir(zoom_path)):
            x_path = zoom_path / x
            if not x_path.is_dir() or not x.isdigit():
                continue

            for y_file in sorted(os.listdir(x_path)):
                if not y_file.endswith(".png"):
                    continue
                y = os.path.splitext(y_file)[0]
                tile_url = f"{base_url}/{tiles_dir.name}/{zoom}/{x}/{y}.png"
                print(f"🔗 Checking: {tile_url}")
                total += 1
                try:
                    r = requests.get(tile_url)
                    if r.status_code != 200:
                        print(f"❌ FAILED ({r.status_code}): {tile_url}")
                        failed += 1
                except Exception as e:
                    print(f"❌ EXCEPTION: {tile_url} — {e}")
                    failed += 1

    print("\n✅ Done.")
    print(f"📦 Total tiles checked: {total}")
    print(f"❌ Failed requests     : {failed}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tests/test_tile_serving.py web/tiles/tiles_N")
        sys.exit(1)

    tiles_path = Path(sys.argv[1])
    if not tiles_path.is_dir():
        print(f"❌ Not a directory: {tiles_path}")
        sys.exit(1)

    test_serving(tiles_path)
