#!/usr/bin/env python3
import os
from PIL import Image, ImageChops

TILES_ROOT = "web/tiles"  # Relative to project root

blank_tiles = []
total_tiles = 0

def is_blank(img):
    # Create a blank image with the same mode and size
    blank = Image.new(img.mode, img.size)
    return ImageChops.difference(img, blank).getbbox() is None

for dirpath, _, filenames in os.walk(TILES_ROOT):
    for filename in filenames:
        if filename.endswith(".png"):
            path = os.path.join(dirpath, filename)
            try:
                img = Image.open(path)
                total_tiles += 1
                if is_blank(img):
                    blank_tiles.append(path)
            except Exception as e:
                print(f"❌ Error reading {path}: {e}")

# Output results
print(f"\n📊 Summary:")
print(f"🔹 Total tiles scanned: {total_tiles}")
print(f"🔸 Blank tiles found: {len(blank_tiles)}")
print(f"✅ Non-blank tiles: {total_tiles - len(blank_tiles)}")

if blank_tiles:
    print("\n🧾 Blank tile paths:")
    for tile in blank_tiles:
        print(f" - {tile}")
