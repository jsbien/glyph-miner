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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = Path(f"logs/test_both_{timestamp}.log")
    log_path.parent.mkdir(exist_ok=True)

    print("=== Restarting server for port 8080 ===")
    run_and_log(["python3", "local/restart-server_docker.py"], log_path=log_path)

    print("=== Uploading to port 8080 ===")
    run_and_log([
        "python3", "batch_upload_pages.py", "8080",
        "--input-dir", "masks",
        "--title", "Opusculum",
        "--collection", "Polonia Typographica"
    ], cwd="utils", log_path=log_path)

    print("=== Restarting Python 3 port via restart-server.sh (port 9090) ===")
    run_and_log(["bash", "local/restart-server.sh"], log_path=log_path)

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
