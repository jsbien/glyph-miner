import requests
from pathlib import Path
from PIL import Image
import argparse
import logging
from datetime import datetime

__version__ = "1.0.5"

API = "http://localhost:9090/api"

# Setup logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = logs_dir / f"upload_log_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def find_or_create_collection(title, dry_run):
    collections = requests.get(f"{API}/collections").json()
    for col in collections:
        if col["title"] == title:
            logger.info(f"[✓] Found existing collection: {title}")
            return col["id"]

    if dry_run:
        logger.info(f"[DRY-RUN] Would create collection: {title}")
        return -1

    logger.info(f"[+] Creating collection: {title}")
    # res = requests.post(f"{API}/collections", json={"title": title})
    # res.raise_for_status()
    # data = res.json()
    res = requests.post(f"{API}/collections", json={"title": title})
    try:
        res.raise_for_status()
        content_type = res.headers.get("Content-Type", "")
        print(f"[DEBUG] Raw response content-type: {content_type}")
        print(f"[DEBUG] Raw response text: {res.text}")
        data = res.json()
    except Exception as e:
        print(f"[DEBUG] Exception while parsing response: {e}")
        print(f"[DEBUG] Response status: {res.status_code}")
        print(f"[DEBUG] Response body: {res.text}")
        raise

    # 🔍 Diagnostic logging
    logger.error(f"[DEBUG] Collection creation response: {data} (type: {type(data)})")
    print(f"[DEBUG] Collection creation response: {data} (type: {type(data)})")


    if isinstance(data, dict) and "id" in data:
        return data["id"]
    elif isinstance(data, list) and data and "id" in data[0]:
        return data[0]["id"]
    else:
        logger.error("Server returned empty or invalid response when creating collection.")
        logger.error(f"Request payload: title={title}")
        logger.error(f"Response body: {data}")
        raise RuntimeError("Collection creation failed unexpectedly. Check backend behavior.")


def create_document(title, dry_run):
    if dry_run:
        logger.info(f"[DRY-RUN] Would create document: {title}")
        return -1
    res = requests.post(f"{API}/images", json={"title": title})
    res.raise_for_status()
    return res.json()["id"]


def upload_image(image_id, path, img_type, dry_run):
    if dry_run:
        logger.info(f"[DRY-RUN] Would upload {img_type} image: {path}")
        return
    with open(path, "rb") as f:
        res = requests.post(f"{API}/images/{image_id}/{img_type}", files={"file": f})
        res.raise_for_status()
    logger.info(f"[+] Uploaded {img_type} image: {path.name}")


def assign_to_collection(image_id, collection_id, dry_run, title, collection_name):
    if dry_run:
        if image_id == -1 or collection_id == -1:
            logger.info(f"[DRY-RUN] Would assign document (not created: {title}) "
                        f"to collection (not created: {collection_name})")
        else:
            logger.info(f"[DRY-RUN] Would assign document {image_id} to collection {collection_id}")
        return
    res = requests.post(f"{API}/memberships", json={"image_id": image_id, "collection_id": collection_id})
    res.raise_for_status()
    logger.info(f"[+] Assigned document {image_id} to collection {collection_id}")


def is_binary_image(path):
    with Image.open(path) as img:
        img = img.convert("L")
        colors = set(img.getdata())
        return colors.issubset({0, 255})


def main():
    parser = argparse.ArgumentParser(description="Batch upload B/W images as multipage documents into Glyph Miner.")
    parser.add_argument("--input-dir", required=True, help="Directory containing images (PNG, JPG, TIFF).")
    parser.add_argument("--title", required=True, help="Base title of the document (used as prefix per page).")
    parser.add_argument("--collection", required=True, help="Name of the collection to create/use.")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes will be made).")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    assert input_dir.is_dir(), f"Not a directory: {input_dir}"
    logger.info(f"Using input directory: {input_dir.resolve()}")

    image_paths = sorted([
        p for ext in ("*.png", "*.PNG", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG", "*.tif", "*.tiff", "*.TIF", "*.TIFF")
        for p in input_dir.glob(ext)
    ])

    logger.info(f"Found {len(image_paths)} image(s) to process.")
    if not image_paths:
        logger.warning("No image files found in input directory. Exiting.")
        return

    collection_id = find_or_create_collection(args.collection, args.dry_run)

    count_skipped = 0
    count_uploaded = 0

    for bw_img in image_paths:
        page_number = bw_img.stem.split("-")[-1]
        title = f"{args.title} - Page {page_number}"

        doc_id = create_document(title, args.dry_run)

        if not is_binary_image(bw_img):
            logger.warning(f"[!] Skipping {bw_img.name}: not binary")
            count_skipped += 1
            continue

        upload_image(doc_id, bw_img, "color", args.dry_run)
        upload_image(doc_id, bw_img, "binarized", args.dry_run)
        assign_to_collection(doc_id, collection_id, args.dry_run, title, args.collection)
        logger.info(f"[✓] Uploaded: {title}")
        count_uploaded += 1

    logger.info("========== Summary ==========")
    logger.info(f"Total images found      : {len(image_paths)}")
    logger.info(f"Uploaded (or simulated) : {count_uploaded}")
    logger.info(f"Skipped (non-binary)    : {count_skipped}")
    logger.info("=============================")


if __name__ == "__main__":
    main()
