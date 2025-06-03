#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import math
import sys
from PIL import Image

def create_tiles(image_path, base_path, verbose=0):
    """
    Generates tile pyramid for the image at image_path, storing tiles under base_path.
    Tiles are 256x256 by default.
    """
    tile_size = (256, 256)
    os.makedirs(base_path, exist_ok=True)

    # Open the image
    img = Image.open(image_path)
    image_width, image_height = img.size

    if verbose:
        print(f"[INFO] Input image size: {image_width}x{image_height}")

    # Calculate the number of columns and rows at base zoom level (zoom level 0)
    tile_width, tile_height = tile_size
    cols = int(math.ceil(image_width / tile_width))
    rows = int(math.ceil(image_height / tile_height))

    # Determine maximum zoom level
    max_zoom = int(max(math.ceil(math.log(cols, 2)),
                        math.ceil(math.log(rows, 2))))
    if verbose:
        print(f"[INFO] Max zoom level: {max_zoom} (cols={cols}, rows={rows})")

    # Generate tiles for each zoom level
    for z in range(max_zoom + 1):
        scale = 2 ** (max_zoom - z)
        zoom_width = int(math.ceil(image_width / scale))
        zoom_height = int(math.ceil(image_height / scale))

        if verbose:
            print(f"[INFO] Zoom level {z}: scaled size = {zoom_width}x{zoom_height}")

        # Resize the image
        zoom_img = img.resize((zoom_width, zoom_height), Image.LANCZOS)

        # Calculate number of tiles
        cols_z = int(math.ceil(zoom_width / tile_width))
        rows_z = int(math.ceil(zoom_height / tile_height))

        for x in range(cols_z):
            for y in range(rows_z):
                left = x * tile_width
                upper = y * tile_height
                right = min(left + tile_width, zoom_width)
                lower = min(upper + tile_height, zoom_height)

                tile = zoom_img.crop((left, upper, right, lower))
                tile_dir = os.path.join(base_path, str(z), str(x))
                os.makedirs(tile_dir, exist_ok=True)
                tile_path = os.path.join(tile_dir, f"{y}.png")
                tile.save(tile_path)

                if verbose >= 2:
                    print(f"[DEBUG] Saved tile: zoom {z}, x {x}, y {y}")

    if verbose:
        print("[INFO] Tile pyramid generation completed for:", image_path)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 img2tiles.py <image_path> <base_path> [verbose_level]")
        sys.exit(1)

    image_path = sys.argv[1]
    base_path = sys.argv[2]
    verbose_level = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    create_tiles(image_path, base_path, verbose=verbose_level)
