#!/usr/bin/env python3
import requests
from pathlib import Path
from PIL import Image
import argparse
import logging
from datetime import datetime

__version__ = "2.0.0"

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

# Metadata from slides (simplified)
COLLECTION_NAME = "Sebastian Brant: Narrenschiff (Basel, 1494)"
DOCUMENT_TITLE = "Das Narrenschiff"
YEAR = 1494
AUTHOR = "Sebastian Brant"


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
    return res.json().get("id", -1)


def create_document(title, dry_run, api):
    payload = {
        "title": title,
        "author": AUTHOR,
        "year": YEAR
    }
    if dry_run:
        logger.info(f"[DRY-RUN] Would create document: {title}")
        return -1
    res = requests.post(f"{api}/images", json=payload)
    res.raise_for_status()
    return res.json()["id"]


def upload_image(image_id, path, img_type, dry_run, api):
    if dry_run:
        logger.info(f"[DRY-RUN] Would upload {img_type} image: {path.name}")
        return
    with open(path, "rb") as f:
        res = requests.post(f"{api}/images/{image_id}/{img_type}", files={"file": f})
        res.raise_for_status()
    logger.info(f"[+] Uploaded {img_type}: {path.name}")


def assign_to_collection(image_id, collection_id, dry_run, title, collection_name, api):
    if dry_run:
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


def main():
    parser = argparse.ArgumentParser(description="Upload Das Narrenschiff image batch to Glyph Miner.")
    parser.add_argument("port", help="Port number (e.g., 9090)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without uploading anything.")
    args = parser.parse_args()

    api = f"http://localhost:{args.port}/api"

    color_dir = Path("tests/Narrenshiff/color")
    bw_dir = Path("tests/Narrenshiff/bw")

    assert color_dir.is_dir(), f"Missing dir: {color_dir}"
    assert bw_dir.is_dir(), f"Missing dir: {bw_dir}"

    all_bw = sorted(bw_dir.glob("*.tif*"))
    all_color = sorted(color_dir.glob("*.tif*"))

    if len(all_bw) != len(all_color):
        logger.warning(f"[!] Number of BW images ({len(all_bw)}) and color images ({len(all_color)}) differs")

    logger.info(f"→ Found {len(all_bw)} BW + {len(all_color)} color images")

    collection_id = find_or_create_collection(COLLECTION_NAME, args.dry_run, api)

    count_uploaded = 0
    for bw_path, color_path in zip(all_bw, all_color):
        filename = bw_path.stem  # e.g., 0001v
        title = f"{DOCUMENT_TITLE} - Page {filename}"

        if not is_binary_image(bw_path):
            logger.warning(f"[!] Skipping {bw_path.name}: not binary")
            continue

        doc_id = create_document(title, args.dry_run, api)
        upload_image(doc_id, color_path, "color", args.dry_run, api)
        upload_image(doc_id, bw_path, "binarized", args.dry_run, api)
        assign_to_collection(doc_id, collection_id, args.dry_run, title, COLLECTION_NAME, api)

        logger.info(f"[✓] Uploaded {title}")
        count_uploaded += 1

    logger.info("========== Summary ==========")
    logger.info(f"Total uploaded          : {count_uploaded}")
    logger.info("=============================")


if __name__ == "__main__":
    main()
