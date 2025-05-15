#!/usr/bin/env python3

import os
import json
import requests
import argparse
from datetime import datetime

API_BASE = "http://localhost:9090"

def find_or_create_collection(title, dry_run=False):
    """Return the collection ID for the given title. Create it if needed."""
    base_url = f"{API_BASE}/api/collections"

    # Step 1: Fetch existing collections
    try:
        res = requests.get(base_url)
        res.raise_for_status()
        collections = res.json()
        for col in collections:
            if col["title"] == title:
                print(f"[INFO] Found existing collection: {title} (id: {col['id']})")
                return col["id"]
    except Exception as e:
        print(f"[ERROR] Failed to fetch collections: {e}")
        raise

    # Step 2: If not found, create it
    if dry_run:
        print(f"[DRY RUN] Would create collection: {title}")
        return -1

    payload = {"title": title}
    headers = {"Content-Type": "application/json"}
    try:
        res = requests.post(base_url, data=json.dumps(payload), headers=headers)
        res.raise_for_status()
        response_data = res.json()
        collection_id = response_data.get("id")
        if not collection_id:
            raise RuntimeError("Collection creation failed: ID missing in response.")
        print(f"[INFO] Created new collection: {title} (id: {collection_id})")
        return collection_id
    except Exception as e:
        print(f"[ERROR] Failed to create collection: {e}")
        raise

def create_document(title, collection_id, dry_run=False):
    url = f"{API_BASE}/api/images"
    payload = {
        "title": title,
        "subtitle": None,
        "author": None,
        "year": None,
        "signature": None
#        "collection_id": collection_id
    }
    headers = {"Content-Type": "application/json"}

    if dry_run:
        print(f"[DRY RUN] Would create document with title: {title}, collection ID: {collection_id}")
        return -1

    res = requests.post(url, data=json.dumps(payload), headers=headers)

    # 🔍 Add this
    print(f"[DEBUG] Status Code: {res.status_code}")
    print(f"[DEBUG] Response Body: {res.text}")

    res.raise_for_status()
    data = res.json()
    return data.get("id")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--collection", "-c", type=str, default="Polonia Typographica",
        help="Name of the collection to use or create"
    )
    parser.add_argument(
        "--title", "-t", type=str, required=True,
        help="Title of the document to create"
    )
    parser.add_argument(
        "--input-dir", "-i", type=str, required=True,
        help="Directory containing input images (currently unused)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Dry run without POSTing")
    args = parser.parse_args()

    print(f"[INFO] Using input directory: {args.input_dir}")
    print(f"[INFO] Found 1 image(s) to process.")
    print(f"[INFO] [+] Creating collection: {args.collection}")
    
    collection_id = find_or_create_collection(args.collection, args.dry_run)

    doc_id = create_document(args.title, collection_id, args.dry_run)
    print(f"[INFO] Created document ID: {doc_id}")

if __name__ == "__main__":
    main()
