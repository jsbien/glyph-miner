#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path

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
            print(line, end="")       # live console output
            log_file.write(line)      # duplicate to log
    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)

def main():
    VERSION = "test-server.py v1.0"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = Path(f"logs/test_server_{timestamp}.log")
    log_path.parent.mkdir(exist_ok=True)

    # Log to both file and console
    log_file = open(log_path, "w", encoding="utf-8")
    tee = lambda text: (print(text), log_file.write(text + "\n"))
    tee(f"📄 Logging to: {log_path}")
    tee(f"🧪 {VERSION}")
    tee(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Get current commit hash (short)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
        tee(f"🔢 Commit: {commit}")
    except Exception as e:
        tee(f"❌ Could not get commit hash: {e}")

    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # log_path = Path(f"logs/test_server1_{timestamp}.log")
    # log_path.parent.mkdir(exist_ok=True)

    print("=== Restarting Python 3 port via restart-server.sh (port 9090) ===")
    run_and_log(["bash", "local/restart-server.sh"], log_path=log_path)

    print("🧹 Clearing collections table...")

    try:
        result = subprocess.run(
            ["curl", "-X", "POST", "-s", "http://localhost:9090/api/debug/clear"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            print("❌ Failed to clear collections via debug endpoint")
        else:
            print("✅ Collections cleared")
    except Exception as e:
        print(f"❌ Error during curl request: {e}")

        # Remove and recreate local directories with .gitkeep
    from shutil import rmtree

    def reset_dir(path):
        dir_path = Path(path)
        if dir_path.exists():
            print(f"🧹 Removing {dir_path}")
            rmtree(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / ".gitkeep").touch()
        print(f"📁 Recreated {dir_path} with .gitkeep")

    reset_dir("web/synthetic_pages")
    reset_dir("web/thumbnails")
    reset_dir("web/tiles")
        
    print("=== Uploading to port 9090 ===")
    run_and_log([
        "python3", "batch_upload_pages.py", "9090",
        "--input-dir", "masks",
        "--title", "Opusculum",
        "--collection", "Polonia Typographica"
    ], cwd="utils", log_path=log_path)

    print(f"\n✅ All done. Log saved to {log_path}")

if __name__ == "__main__":
    main()
