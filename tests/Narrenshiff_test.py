#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path
import shutil
import sys

def run_and_log(cmd, cwd=None, log_path=None, env=None):
    cmd_display = " ".join(str(c) for c in cmd)
    print(f"\n🚀 Running: {cmd_display}\n")
    with subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, env=env
    ) as proc:
        with open(log_path, "a", encoding="utf-8") as logf:
            for line in proc.stdout:
                print(line, end="")
                logf.write(line)
        if proc.wait() != 0:
            raise RuntimeError(f"Command failed: {cmd_display}")

def main():
    # Prepare logs/
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Generate unique run ID
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"{commit}_{timestamp}"

    log_path = logs_dir / f"test-run-{run_id}.log"
    print(f"📄 Logging to: {log_path.resolve()}")

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

    # Restart server with run ID passed to uwsgi
    run_and_log(["bash", "local/restart-server.sh", run_id], log_path=log_path)

    # Upload documents (from outside the repo!)
    run_and_log([
        "python3", "Narrenshiff_upload.py", "9090", f"--run-id={run_id}"
    ], cwd="tests", log_path=log_path)

if __name__ == "__main__":
    main()
