#!/usr/bin/env python3
import requests
from pathlib import Path
import argparse
import logging
from datetime import datetime
from PIL import Image

__version__ = "1.1.0"

# Setup logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = logs_dir / f"upload_narrenshiff_{timestamp}.log"

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

    if isinstance(data, dict) and "id" in data:
        return data["id"]
    elif isinstance(data, list) and data and "id" in data[0]:
        return data[0]["id"]
    else:
        logger.error("Server returned empty or invalid response when creating collection.")
        logger.error(f"Request payload: title={title}")
        logger.error(f"Response body: {data}")
        raise RuntimeError("Collection creation failed unexpectedly. Check backend behavior.")


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
        logger.info(f"[DRY-RUN] Would assign doc {image_id} to collection {collection_id}")
        return
    res = requests.post(f"{api}/memberships", json={
        "image_id": image_id,
        "collection_id": collection_id
    })
    res.raise_for_status()
    logger.info(f"[+] Assigned document {image_id} to collection {collection_id}")


def is_binary_image(path):
    with Image.open(path) as img:
        img = img.convert("L")
        colors = set(img.getdata())
        return colors.issubset({0, 255})


def main():
    parser = argparse.ArgumentParser(description="Upload Das Narrenschiff page images.")
    parser.add_argument("port", help="Port number of the running Glyph Miner server (e.g., 8080)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without modifying anything.")
    args = parser.parse_args()

    api = f"http://localhost:{args.port}/api"
    collection_title = "Das Narrenschiff"
    base_title = "Das Narrenschiff"

    color_dir = Path("tests/Narrenshiff/color")
    bw_dir = Path("tests/Narrenshiff/bw")

    assert color_dir.is_dir(), f"Missing dir: {color_dir}"
    assert bw_dir.is_dir(), f"Missing dir: {bw_dir}"

    logger.info(f"Using color images from: {color_dir.resolve()}")
    logger.info(f"Using binary images from: {bw_dir.resolve()}")

    collection_id = find_or_create_collection(collection_title, args.dry_run, api)

    color_images = sorted(color_dir.glob("*.tif*"))
    count_uploaded = 0
    count_skipped = 0

    for color_img in color_images:
        page_stem = color_img.stem
        bw_img = bw_dir / f"{page_stem}.tiff"

        if not bw_img.exists():
            logger.warning(f"[!] No matching B/W image for {page_stem}. Skipping.")
            count_skipped += 1
            continue

        title = f"{base_title} - Page {page_stem}"
        doc_id = create_document(title, args.dry_run, api)

        upload_image(doc_id, color_img, "color", args.dry_run, api)
        upload_image(doc_id, bw_img, "binarized", args.dry_run, api)

        assign_to_collection(doc_id, collection_id, args.dry_run, title, collection_title, api)

        logger.info(f"[✓] Uploaded: {title}")
        count_uploaded += 1

    logger.info("========== Summary ==========")
    logger.info(f"Color images processed   : {len(color_images)}")
    logger.info(f"Uploaded successfully    : {count_uploaded}")
    logger.info(f"Skipped (missing B/W)    : {count_skipped}")
    logger.info("=============================")


if __name__ == "__main__":
    main()
