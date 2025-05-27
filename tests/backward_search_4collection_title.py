#!/usr/bin/env python3
import subprocess
import requests
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from PIL import Image

# ========== Configuration ==========
PORT = "9090"
API = f"http://localhost:{PORT}/api"
REPO_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
TEST_IMAGE = Path("tests/test.png")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
TIMESTAMP = datetime.now().strftime('%Y%m%d-%H%M%S')
LOG_FILE = LOG_DIR / f"backward-search-{TIMESTAMP}.log"

RUN_UWSGI = ["local/run-uwsgi.sh"]
KILL_UWSGI = ["local/kill-uwsgi.sh"]

# ========== Logging ==========
def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# ========== Git Utilities ==========
def run_git(*args):
    return subprocess.check_output(["git"] + list(args), text=True).strip()

def get_original_ref():
    try:
        return run_git("symbolic-ref", "--quiet", "--short", "HEAD")
    except subprocess.CalledProcessError:
        return run_git("rev-parse", "HEAD")

def checkout(commit):
    subprocess.run(["git", "checkout", "-f", commit], check=True)

# ========== UWSGI Control ==========
def start_server():
    subprocess.run(RUN_UWSGI, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

def stop_server():
    subprocess.run(KILL_UWSGI, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

def wait_until_ready(timeout=15):
    for _ in range(timeout * 2):
        try:
            r = requests.get(f"{API}/collections")
            if r.status_code == 200:
                return True
        except:
            time.sleep(0.5)
    return False

# ========== Setup ==========
def create_test_image():
    TEST_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    if not TEST_IMAGE.exists():
        Image.new("1", (20, 20), 1).save(TEST_IMAGE)

def clear_backend():
    try:
        r = requests.post(f"{API}/debug/clear")
        r.raise_for_status()
        log("🧹 Backend cleared")
    except Exception as e:
        log(f"[ERROR] Could not clear backend: {e}")

# ========== Upload Logic ==========
def create_collection(title):
    r = requests.post(f"{API}/collections", json={"title": title})
    r.raise_for_status()
    return r.json()["id"]

def create_document(title):
    r = requests.post(f"{API}/images", json={"title": title})
    r.raise_for_status()
    return r.json()["id"]

def upload_image(image_id, path, kind):
    with open(path, "rb") as f:
        r = requests.post(f"{API}/images/{image_id}/{kind}", files={"file": f})
        r.raise_for_status()

def assign_membership(image_id, collection_id):
    r = requests.post(f"{API}/memberships", json={"image_id": image_id, "collection_id": collection_id})
    r.raise_for_status()

# ========== Main Flow ==========
def main():
    os.chdir(REPO_DIR)
    create_test_image()
    original_ref = get_original_ref()
    log(f"🔁 Starting backward search from: {original_ref}")
    commits = run_git("rev-list", "--reverse", "HEAD").splitlines()

    try:
        for commit in commits:
            log(f"\n🔍 Checking commit {commit}")
            checkout(commit)

            start_server()
            if not wait_until_ready():
                log("❌ Server failed to start")
                stop_server()
                continue

            try:
                clear_backend()
                collection_id = create_collection("Das Narrenschiff")
                image_id = create_document("Test Page")
                upload_image(image_id, TEST_IMAGE, "color")
                upload_image(image_id, TEST_IMAGE, "binarized")
                assign_membership(image_id, collection_id)

                print("\n🌐 Test environment is ready.")
                print("👉 Please open http://localhost:9090/#/viewer/collection/1/image/1")
                print("📝 Enter result for commit", commit)
                print("    [0] PASS — title shown")
                print("    [1] FAIL — title missing")
                print("    [q] Quit")

                verdict = input("🔍 Verdict (0/1/q): ").strip()
                if verdict == "q":
                    log("🛑 User aborted the search.")
                    break
                elif verdict == "0":
                    log(f"✅ PASS at commit {commit}")
                elif verdict == "1":
                    log(f"❌ FAIL at commit {commit}")
                else:
                    log(f"❓ Unknown input at commit {commit}: {verdict}")

            except Exception as e:
                log(f"[EXCEPTION] {e}")
            finally:
                stop_server()
    finally:
        log(f"\n🔁 Restoring original ref: {original_ref}")
        checkout(original_ref)
        log("✅ Ref restored")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import subprocess
import requests
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from PIL import Image

# ========== Configuration ==========
PORT = "9090"
API = f"http://localhost:{PORT}/api"
REPO_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
TEST_IMAGE = Path("tests/test.png")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
TIMESTAMP = datetime.now().strftime('%Y%m%d-%H%M%S')
LOG_FILE = LOG_DIR / f"backward-search-{TIMESTAMP}.log"

RUN_UWSGI = ["local/run-uwsgi.sh"]
KILL_UWSGI = ["local/kill-uwsgi.sh"]

# ========== Logging ==========
def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# ========== Git Utilities ==========
def run_git(*args):
    return subprocess.check_output(["git"] + list(args), text=True).strip()

def get_original_ref():
    try:
        return run_git("symbolic-ref", "--quiet", "--short", "HEAD")
    except subprocess.CalledProcessError:
        return run_git("rev-parse", "HEAD")

def checkout(commit):
    subprocess.run(["git", "checkout", "-f", commit], check=True)

# ========== UWSGI Control ==========
def start_server():
    subprocess.run(RUN_UWSGI, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

def stop_server():
    subprocess.run(KILL_UWSGI, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

def wait_until_ready(timeout=15):
    for _ in range(timeout * 2):
        try:
            r = requests.get(f"{API}/collections")
            if r.status_code == 200:
                return True
        except:
            time.sleep(0.5)
    return False

# ========== Setup Helpers ==========
def create_test_image():
    TEST_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    if not TEST_IMAGE.exists():
        Image.new("1", (20, 20), 1).save(TEST_IMAGE)

def clear_backend():
    try:
        r = requests.post(f"{API}/debug/clear")
        r.raise_for_status()
        log("🧹 Backend cleared")
    except Exception as e:
        log(f"[ERROR] Could not clear backend: {e}")

# ========== Upload Flow (from test_server.py) ==========
def create_collection(title):
    r = requests.post(f"{API}/collections", json={"title": title})
    r.raise_for_status()
    return r.json()["id"]

def create_document(title):
    r = requests.post(f"{API}/images", json={"title": title})
    r.raise_for_status()
    return r.json()["id"]

def upload_image(image_id, path, kind):
    with open(path, "rb") as f:
        r = requests.post(f"{API}/images/{image_id}/{kind}", files={"file": f})
        r.raise_for_status()

def assign_membership(image_id, collection_id):
    r = requests.post(f"{API}/memberships", json={"image_id": image_id, "collection_id": collection_id})
    r.raise_for_status()

def verify_collection_title(expected_title="Das Narrenschiff"):
    try:
        r = requests.get(f"{API}/collections")
        r.raise_for_status()
        for c in r.json():
            if c.get("title") == expected_title:
                return True
    except Exception as e:
        log(f"[ERROR] Verification failed: {e}")
    return False

# ========== Main ==========

def main():

COMMIT_LIST = Path("commit-list.txt")
if not COMMIT_LIST.exists():
    log("📜 Writing commit list to commit-list.txt")
    with open(COMMIT_LIST, "w", encoding="utf-8") as f:
        f.write(run_git("rev-list", "--reverse", "HEAD") + "\n")

    os.chdir(REPO_DIR)
    create_test_image()
    original_ref = get_original_ref()
    log(f"🔁 Starting backward search from: {original_ref}")
    with open(COMMIT_LIST, "r", encoding="utf-8") as f:
        commits = [line.strip() for line in f if line.strip()]
#   commits = run_git("rev-list", "--reverse", "HEAD").splitlines()

    try:
        for commit in commits:
            log(f"\n🔍 Checking commit {commit}")
            checkout(commit)

            start_server()
            if not wait_until_ready():
                log("❌ Server failed to start")
                stop_server()
                continue

            try:
                clear_backend()
                collection_id = create_collection("Das Narrenschiff")
                image_id = create_document("Test Page")
                upload_image(image_id, TEST_IMAGE, "color")
                upload_image(image_id, TEST_IMAGE, "binarized")
                assign_membership(image_id, collection_id)

                if verify_collection_title():
                    log(f"✅ Title OK at commit {commit}")
                else:
                    log(f"🚫 Missing title at commit {commit}")
            except Exception as e:
                log(f"[EXCEPTION] {e}")
            finally:
                stop_server()
    finally:
        log(f"\n🔁 Restoring original ref: {original_ref}")
        checkout(original_ref)
        log("✅ Ref restored")

if __name__ == "__main__":
    main()
