#!/usr/bin/env python3
import os
import sys
from PIL import Image

def reconstruct_all_zoom_levels(tiles_dir, output_base):
    zoom_levels = sorted([int(z) for z in os.listdir(tiles_dir) if z.isdigit()])
    if not zoom_levels:
        raise ValueError(f"No zoom levels found in {tiles_dir}")

    for zoom in zoom_levels:
        zoom_dir = os.path.join(tiles_dir, str(zoom))

        max_x = max_y = -1
        tile_map = {}

        for x_str in os.listdir(zoom_dir):
            x_dir = os.path.join(zoom_dir, x_str)
            if not x_str.isdigit() or not os.path.isdir(x_dir):
                continue
            x = int(x_str)
            for y_file in os.listdir(x_dir):
                if not y_file.endswith(".png"):
                    continue
                y = int(os.path.splitext(y_file)[0])
                tile_map[(x, y)] = os.path.join(x_dir, y_file)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

        if not tile_map:
            print(f"⚠️  No tiles found at zoom level {zoom}")
            continue

        # Get tile size
        sample_tile = Image.open(next(iter(tile_map.values())))
        tile_w, tile_h = sample_tile.size

        full_w = (max_x + 1) * tile_w
        full_h = (max_y + 1) * tile_h
        full_image = Image.new("RGB", (full_w, full_h))

        for (x, y), path in tile_map.items():
            tile = Image.open(path)
            full_image.paste(tile, (x * tile_w, y * tile_h))

        out_file = f"{output_base}_zoom{zoom}.png"
        full_image.save(out_file)
        print(f"✅ Saved: {out_file}  ({full_w}x{full_h}, {len(tile_map)} tiles)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tests/reconstruct_from_tiles.py web/tiles/tiles_N")
        sys.exit(1)

    tiles_path = sys.argv[1]
    if not os.path.isdir(tiles_path):
        print(f"❌ Not a directory: {tiles_path}")
        sys.exit(1)

    image_id = os.path.basename(tiles_path).replace("tiles_", "")
    output_prefix = f"reconstructed_{image_id}"

    reconstruct_all_zoom_levels(tiles_path, output_prefix)
