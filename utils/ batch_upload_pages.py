import requests
from pathlib import Path
from PIL import Image
import argparse

API = "http://localhost:9090/api"

def find_or_create_collection(title, dry_run):
    collections = requests.get(f"{API}/collections").json()
    for col in collections:
        if col["title"] == title:
            print(f"[✓] Found existing collection: {title}")
            return col["id"]
    if dry_run:
        print(f"[DRY-RUN] Would create collection: {title}")
        return -1
    res = requests.post(f"{API}/collections", json={"title": title})
    res.raise_for_status()
    print(f"[+] Created collection: {title}")
    return res.json()["id"]

def create_document(title, dry_run):
    if dry_run:
        print(f"[DRY-RUN] Would create document: {title}")
        return -1
    res = requests.post(f"{API}/images", json={"title": title})
    res.raise_for_status()
    return res.json()["id"]

def upload_image(image_id, path, img_type, dry_run):
    if dry_run:
        print(f"[DRY-RUN] Would upload {img_type} image: {path}")
        return
    with open(path, "rb") as f:
        res = requests.post(f"{API}/images/{image_id}/{img_type}", files={"file": f})
        res.raise_for_status()

def assign_to_collection(image_id, collection_id, dry_run):
    if dry_run:
        print(f"[DRY-RUN] Would assign document {image_id} to collection {collection_id}")
        return
    res = requests.post(f"{API}/memberships", json={"image_id": image_id, "collection_id": collection_id})
    res.raise_for_status()

def is_binary_image(path):
    with Image.open(path) as img:
        img = img.convert("L")
        colors = set(img.getdata())
        return colors.issubset({0, 255})

def main():
    parser = argparse.ArgumentParser(description="Batch upload B/W images as multipage documents into Glyph Miner.")
    parser.add_argument("--input-dir", required=True, help="Directory containing B/W PNG images.")
    parser.add_argument("--title", required=True, help="Base title of the document (used as prefix per page).")
    parser.add_argument("--collection", required=True, help="Name of the collection to create/use.")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes will be made).")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    assert input_dir.is_dir(), f"Not a directory: {input_dir}"

    collection_id = find_or_create_collection(args.collection, args.dry_run)

    for bw_img in sorted(input_dir.glob("*.png")):
        page_number = bw_img.stem.split("-")[-1]
        title = f"{args.title} - Page {page_number}"

        doc_id = create_document(title, args.dry_run)

        if not is_binary_image(bw_img):
            print(f"[!] Skipping {bw_img}: not binary")
            continue

        upload_image(doc_id, bw_img, "color", args.dry_run)
        upload_image(doc_id, bw_img, "binarized", args.dry_run)
        assign_to_collection(doc_id, collection_id, args.dry_run)
        print(f"[✓] Uploaded: {title}")

if __name__ == "__main__":
    main()
