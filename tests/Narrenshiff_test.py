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

    # Clean previous database and uploads
    print("🧹 Cleaning previous run data...")
    for sub in ("web/synthetic_pages", "web/thumbnails", "web/tiles"):
        path = Path(sub)
        for child in path.iterdir():
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)

    # Restart server with run ID passed to uwsgi
    run_and_log(["bash", "local/restart-server.sh", run_id], log_path=log_path)

    # Upload documents (from outside the repo!)
    run_and_log([
        "python3", "Narrenshiff_upload.py", "9090"
    ], cwd="tests", log_path=log_path)

if __name__ == "__main__":
    main()
