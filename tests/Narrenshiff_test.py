#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path
from shutil import rmtree

def run_and_log(command, cwd=None, log_path=None):
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    with open(log_path, "a", encoding="utf-8") as log_file:
        for line in process.stdout:
            print(line, end="")
            log_file.write(line)
    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)

def reset_dir(path):
    dir_path = Path(path)
    if dir_path.exists():
        print(f"🧹 Removing {dir_path}")
        rmtree(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    (dir_path / ".gitkeep").touch()
    print(f"📁 Recreated {dir_path} with .gitkeep")

def main():
    VERSION = "Narrenshiff_test.py v1.0"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = Path(f"logs/test-{timestamp}.log")
    log_path.parent.mkdir(exist_ok=True)

    # Log to both file and console
    print(f"📄 Logging to: {log_path}")
    exec_log = open(log_path, "w", encoding="utf-8")
    tee = lambda text: (print(text), exec_log.write(text + "\n"))
    tee(f"🧪 {VERSION}")
    tee(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
        tee(f"🔢 Commit: {commit}")
    except Exception as e:
        tee(f"❌ Could not get commit hash: {e}")

    print("=== Restarting server on port 9090 ===")
    run_and_log(["bash", "local/restart-server.sh"], log_path=log_path)

    print("🧹 Clearing backend database via debug endpoint...")
    try:
        result = subprocess.run(
            ["curl", "-X", "POST", "-s", "http://localhost:9090/api/debug/clear"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            print("❌ Failed to clear collections")
        else:
            print("✅ Cleared database")
    except Exception as e:
        print(f"❌ curl error: {e}")

    # Clean directories
    reset_dir("web/synthetic_pages")
    reset_dir("web/thumbnails")
    reset_dir("web/tiles")

    print("=== Uploading Das Narrenschiff test set ===")
    run_and_log([
        "python3", "tests/Narrenshiff_upload.py", "9090"
    ], log_path=log_path)

    print(f"\n✅ All done. Log saved to {log_path}")

if __name__ == "__main__":
    main()
