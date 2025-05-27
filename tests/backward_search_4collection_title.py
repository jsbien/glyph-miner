#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import requests
import shutil

REPO_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
os.chdir(REPO_DIR)

original_ref = subprocess.run(
    ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
).stdout.strip()

if not original_ref:
    original_ref = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

print(f"🔁 Returning to original ref: {original_ref}")

commit_list_path = Path("commit-list.txt")
with open(commit_list_path, "r") as f:
    commits = [line.strip() for line in f if line.strip()]

result_file = Path("search-results.txt")
results = {}
if result_file.exists():
    with open(result_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                results[parts[0]] = parts[1]

def run(cmd, cwd=None):
    print(f"▶️ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)

def run_and_log(cmd, cwd=None, log_path=None):
    with open(log_path, "a") as log:
        subprocess.run(cmd, cwd=cwd, stdout=log, stderr=log, check=True)

def log(msg):
    print(f"[LOG] {msg}")

def run_test(port, log_path):
    api = f"http://localhost:{port}/api"
    image_dir = Path("../Narrenshiff")
    bw_dir = image_dir / "bw"
    color_dir = image_dir / "color"

    assert bw_dir.exists(), f"Missing directory: {bw_dir}"
    assert color_dir.exists(), f"Missing directory: {color_dir}"

    def post_json(url, payload):
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def upload_image(img_id, path, kind):
        with open(path, "rb") as f:
            res = requests.post(f"{api}/images/{img_id}/{kind}", files={"file": f})
            res.raise_for_status()

    def clear_backend():
        try:
            requests.post(f"{api}/debug/clear")
        except Exception as e:
            print(f"[!] Clear failed: {e}")

    clear_backend()
    collection_title = "Das Narrenschiff"
    collection_id = post_json(f"{api}/collections", {"title": collection_title})["id"]

    # Sort filenames: 0001v.tiff < 0001r.tiff
    color_pages = sorted(color_dir.glob("*.tif*"), key=lambda p: (p.stem[:-1], p.stem[-1]))
    bw_pages = sorted(bw_dir.glob("*.tif*"), key=lambda p: (p.stem[:-1], p.stem[-1]))

    for bw, col in zip(bw_pages, color_pages):
        stem = bw.stem
        title = f"{collection_title} - Page {stem}"
        image = post_json(f"{api}/images", {"title": title})
        img_id = image["id"]
        upload_image(img_id, col, "color")
        upload_image(img_id, bw, "binarized")
        post_json(f"{api}/memberships", {"image_id": img_id, "collection_id": collection_id})

    with open(log_path, "a") as log:
        log.write(f"[✓] Uploaded {len(bw_pages)} pages into '{collection_title}'\n")

# Begin loop
for commit in commits:
    if commit in results:
        log(f"⏩ Skipping already tested commit {commit}")
        continue

    run(["git", "checkout", commit])
    print(f"\n🔍 Now testing commit: {commit}")

    log_path = f"test-output-{commit}.log"
    try:
        run(["./kill-uwsgi.sh"])
    except Exception:
        pass

    run(["./run-uwsgi.sh"])
    try:
        run_test(port="9090", log_path=log_path)
    except Exception as e:
        with open(log_path, "a") as log:
            log.write(f"[!] Error during test: {e}\n")

    try:
        run(["./kill-uwsgi.sh"])
    except Exception:
        pass

    verdict = input(f"📝 Enter result for commit {commit} (0 = PASS, 1 = FAIL, q = quit): ").strip()
    if verdict == "q":
        print("🚪 Quitting...")
        break
    elif verdict not in {"0", "1"}:
        print("⚠️ Invalid input, skipping.")
        continue

    with open(result_file, "a") as f:
        f.write(f"{commit} {verdict}\n")

# Restore
run(["git", "checkout", original_ref])
print(f"✅ Restored to: {original_ref}")
