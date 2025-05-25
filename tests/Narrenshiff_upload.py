#!/usr/bin/env python3
import requests
from pathlib import Path
from PIL import Image
import argparse
import logging
from datetime import datetime
from collections import defaultdict
import re

__version__ = "1.1.0"

# Setup logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = logs_dir / f"narrenshiff_upload_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def find_or_create_collection(title, dry_run, api):
    collections = requests.get(f"{api}/collections").json()
    for col in collections:
        if col["title"] == title:
            logger.info(f"[✓] Found existing collection: {title}")
            return col["id"]

    if dry_run:
        logger.info(f"[DRY-RUN] Would create collection: {title}")
        return -1

    logger.info(f"[+] Creating collection: {title}")
    res = requests.post(f"{api}/collections", json={"title": title})
    res.raise_for_status()
    data = res.json()
    return data["id"] if isinstance(data, dict) else data[0]["id"]


def create_document(title, dry_run, api):
    if dry_run:
        logger.info(f"[DRY-RUN] Would create document: {title}")
        return -1
    res = requests.post(f"{api}/images", json={"title": title})
    res.raise_for_status()
    return res.json()["id"]


def upload_image(image_id, path, img_type, dry_run, api):
    if dry_run:
        logger.info(f"[DRY-RUN] Would upload {img_type} image: {path}")
        return
    with open(path, "rb") as f:
        res = requests.post(f"{api}/images/{image_id}/{img_type}", files={"file": f})
        res.raise_for_status()
    logger.info(f"[+] Uploaded {img_type} image: {path.name}")


def assign_to_collection(image_id, collection_id, dry_run, title, collection_name, api):
    if dry_run:
        if image_id == -1 or collection_id == -1:
            logger.info(f"[DRY-RUN] Would assign document (not created: {title}) "
                        f"to collection (not created: {collection_name})")
        else:
            logger.info(f"[DRY-RUN] Would assign document {image_id} to collection {collection_id}")
        return
    res = requests.post(f"{api}/memberships", json={"image_id": image_id, "collection_id": collection_id})
    res.raise_for_status()
    logger.info(f"[+] Assigned document {image_id} to collection {collection_id}")


def is_binary_image(path):
    with Image.open(path) as img:
        img = img.convert("L")
        colors = set(img.getdata())
        return colors.issubset({0, 255})


def collect_ordered_images(color_dir, bw_dir):
    """
    Collects and returns matched color and binarized files in sorted (0001v, 0001r...) order.
    """
    def group_files(directory):
        grouped = defaultdict(dict)
        for file in directory.glob("*.tif*"):
            match = re.match(r"(\d{4})([vr])", file.stem)
            if match:
                number, side = match.groups()
                grouped[number][side] = file
        return grouped

    color_grouped = group_files(color_dir)
    bw_grouped = group_files(bw_dir)

    ordered_pairs = []
    for number in sorted(bw_grouped.keys()):
        for side in ("v", "r"):
            if side in bw_grouped[number] and side in color_grouped[number]:
                ordered_pairs.append((bw_grouped[number][side], color_grouped[number][side]))
            elif side in bw_grouped[number]:
                logger.warning(f"[!] Missing color match for: {bw_grouped[number][side].name}")
            elif side in color_grouped[number]:
                logger.warning(f"[!] Missing binarized match for: {color_grouped[number][side].name}")
    return ordered_pairs


def main():
    parser = argparse.ArgumentParser(description="Upload Das Narrenschiff pages into Glyph Miner.")
    parser.add_argument("port", help="Port number of the running Glyph Miner server (e.g., 9090)")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes will be made).")
    args = parser.parse_args()

    api = f"http://localhost:{args.port}/api"

    bw_dir = Path("tests/Narrenshiff/bw")
    color_dir = Path("tests/Narrenshiff/color")

    if not bw_dir.is_dir() or not color_dir.is_dir():
        logger.error("Missing required subdirectories: tests/Narrenshiff/bw and /color")
        return

    logger.info("📁 Uploading from: tests/Narrenshiff")
    logger.info("🖼️  Binary images: %s", bw_dir.resolve())
    logger.info("🌈 Color images:  %s", color_dir.resolve())

    collection_name = "Das Narrenschiff"
    collection_id = find_or_create_collection(collection_name, args.dry_run, api)

    pairs = collect_ordered_images(color_dir, bw_dir)
    logger.info(f"📄 Matched and ordered image pairs: {len(pairs)}")

    uploaded = 0
    for bw_img, color_img in pairs:
        page_label = bw_img.stem  # e.g., "0001v"
        title = f"{collection_name} - Page {page_label}"

        if not is_binary_image(bw_img):
            logger.warning(f"[!] Skipping {bw_img.name}: not binary")
            continue

        doc_id = create_document(title, args.dry_run, api)
        upload_image(doc_id, color_img, "color", args.dry_run, api)
        upload_image(doc_id, bw_img, "binarized", args.dry_run, api)
        assign_to_collection(doc_id, collection_id, args.dry_run, title, collection_name, api)
        logger.info(f"[✓] Uploaded page: {page_label}")
        uploaded += 1

    logger.info("========== ✅ Summary ==========")
    logger.info(f"Total page pairs processed: {len(pairs)}")
    logger.info(f"Successfully uploaded       : {uploaded}")
    logger.info("================================")


if __name__ == "__main__":
    main()
