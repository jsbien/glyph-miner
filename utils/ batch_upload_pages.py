import requests
from pathlib import Path
from PIL import Image

API = "http://localhost:9090/api"

def find_or_create_collection(title):
    collections = requests.get(f"{API}/collections").json()
    for col in collections:
        if col["title"] == title:
            return col["id"]
    res = requests.post(f"{API}/collections", json={"title": title})
    res.raise_for_status()
    return res.json()["id"]

def create_document(title):
    res = requests.post(f"{API}/images", json={"title": title})
    res.raise_for_status()
    return res.json()["id"]

def upload_image(image_id, path, img_type):
    with open(path, "rb") as f:
        res = requests.post(f"{API}/images/{image_id}/{img_type}", files={"file": f})
        res.raise_for_status()

def assign_to_collection(image_id, collection_id):
    res = requests.post(f"{API}/memberships", json={"image_id": image_id, "collection_id": collection_id})
    res.raise_for_status()

def is_binary_image(path):
    with Image.open(path) as img:
        img = img.convert("L")
        colors = set(img.getdata())
        return colors.issubset({0, 255})

# === MAIN SCRIPT ===

collection_title = "Old Manuscript"
bw_dir = Path("pages/bw")
collection_id = find_or_create_collection(collection_title)

for bw_img in sorted(bw_dir.glob("*.png")):
    page_number = bw_img.stem.split("-")[-1]
    title = f"{collection_title} - Page {page_number}"
    doc_id = create_document(title)

    if is_binary_image(bw_img):
        upload_image(doc_id, bw_img, "color")
        upload_image(doc_id, bw_img, "binarized")
    else:
        raise ValueError(f"Image {bw_img} is not binary — provide a separate color version")

    assign_to_collection(doc_id, collection_id)
