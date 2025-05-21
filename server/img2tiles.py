#!/usr/bin/env python3

import os
import sys
import math
import argparse
from PIL import Image

def create_tiles(image_path, output_dir, color_flag, verbose=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if verbose:
        print(f"[INFO] Opening image: {image_path}")
    im = Image.open(image_path)
    width, height = im.size

    tile_size = 256
    max_level = math.ceil(math.log2(max(width, height)))

    for level in range(max_level + 1):
        scale = 2 ** (max_level - level)
        level_width = math.ceil(width / scale)
        level_height = math.ceil(height / scale)

        if verbose:
            print(f"[INFO] Generating level {level}: {level_width}x{level_height} tiles")

        resized = im.resize((level_width, level_height), Image.LANCZOS)

        tiles_x = math.ceil(level_width / tile_size)
        tiles_y = math.ceil(level_height / tile_size)

        for x in range(tiles_x):
            for y in range(tiles_y):
                left = x * tile_size
                upper = y * tile_size
                right = min(left + tile_size, resized.width)
                lower = min(upper + tile_size, resized.height)

                tile = resized.crop((left, upper, right, lower))

                tile_dir = os.path.join(output_dir, str(level), str(x))
                os.makedirs(tile_dir, exist_ok=True)
                tile_path = os.path.join(tile_dir, f"{y}.png")
                tile.save(tile_path)

                if verbose:
                    print(f"  ↳ Saved tile {tile_path} ({tile.width}x{tile.height})")

    if verbose:
        print("[DONE] Tile generation complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate tiles from an image.")
    parser.add_argument("input_path", help="Path to the input image")
    parser.add_argument("output_dir", help="Path to the output tile directory")
    parser.add_argument("color_flag", help="Color mode (currently unused)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    create_tiles(args.input_path, args.output_dir, args.color_flag, verbose=args.verbose)
