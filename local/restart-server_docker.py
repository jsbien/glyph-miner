#!/usr/bin/env python3

import subprocess
import argparse
import time
from pathlib import Path

CONTAINER_NAME = "glyphminer"
IMAGE_NAME = "glyphminer/glyphminer"
CID_FILE = Path("/tmp/glyphminer-container.id")

MYSQL_USER = "glyphminer"
MYSQL_PW = "glyphminer"
MYSQL_DB = "glyphminer"


def run(command, check=True, capture_output=False):
    try:
        result = subprocess.run(command, shell=True, check=check,
                                capture_output=capture_output, text=True)
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        if e.stderr:
            print("stderr:", e.stderr.strip())
        elif e.output:
            print("output:", e.output.strip())
        else:
            print("return code:", e.returncode)
        raise


def container_exists(name):
    output = run("docker ps -a --format '{{.Names}}'", capture_output=True)
    return name in output.splitlines()


def container_is_running(name):
    output = run("docker ps --format '{{.Names}}'", capture_output=True)
    return name in output.splitlines()


def stop_and_remove_container(name):
    print(f"Stopping and removing container '{name}'...")
    try:
        run(f"docker stop {name}")
    except subprocess.CalledProcessError:
        pass
    try:
        run(f"docker rm {name}")
    except subprocess.CalledProcessError:
        pass


def truncate_tables(container):
    print("Truncating images and collections tables in running container...")
    query = "TRUNCATE TABLE images; TRUNCATE TABLE collections;"
    run(
        f'docker exec {container} '
        f'mysql -u{MYSQL_USER} -p{MYSQL_PW} -D{MYSQL_DB} '
        f'-e "{query}"'
    )
    print("✅ Tables truncated.")


def release_port_8080():
    print("Checking if port 8080 is already bound...")
    container_ids = run(
        "docker ps --filter 'publish=8080' --format '{{.ID}}'",
        capture_output=True
    ).splitlines()

    if container_ids:
        print(f"⚠️  Port 8080 is in use by {len(container_ids)} container(s). Stopping and removing them...")
        for cid in container_ids:
            try:
                run(f"docker stop {cid}")
                run(f"docker rm {cid}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to stop/remove container {cid}: {e}")
        print("✅ Port 8080 has been freed.")
    else:
        print("✅ Port 8080 is free.")


def start_container(name):
    print("Starting new container...")
    container_id = run(
        f"docker run -d -p 8080:80 --name {name} {IMAGE_NAME}",
        capture_output=True
    )
    print(f"Container started with ID: {container_id}")
    CID_FILE.write_text(container_id + "\n")
    print(f"Saved container ID to {CID_FILE}")
    return container_id


def check_database(container):
    print("Waiting a few seconds for database to initialize...")
    time.sleep(5)

    print("Checking database contents...")
    for table in ["images", "collections"]:
        try:
            count = run(
                f'docker exec {container} '
                f'mysql -u{MYSQL_USER} -p{MYSQL_PW} -D{MYSQL_DB} '
                f'-e "SELECT COUNT(*) FROM {table};"',
                capture_output=True
            )
            lines = count.splitlines()
            if len(lines) >= 2:
                print(f"✅ {table}: {lines[1]} rows")
            else:
                print(f"⚠️  Unexpected response for table {table}: {count}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error checking table {table}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Restart Glyphminer Docker container.")
    parser.add_argument("--reset-db", action="store_true",
                        help="Also remove the Docker image to wipe the database")
    parser.add_argument("--running-action", choices=["kill", "clean"], default="kill",
                        help="What to do if the container is already running (default: kill)")
    args = parser.parse_args()

    if container_is_running(CONTAINER_NAME):
        print(f"Container '{CONTAINER_NAME}' is already running.")
        if args.running_action == "kill":
            stop_and_remove_container(CONTAINER_NAME)
            release_port_8080()
            container_id = start_container(CONTAINER_NAME)
            check_database(CONTAINER_NAME)
        elif args.running_action == "clean":
            truncate_tables(CONTAINER_NAME)
            check_database(CONTAINER_NAME)
        return

    # Container exists but not running
    if container_exists(CONTAINER_NAME):
        stop_and_remove_container(CONTAINER_NAME)

    if args.reset_db:
        run(f"docker rmi {IMAGE_NAME}")

    release_port_8080()
    container_id = start_container(CONTAINER_NAME)
    check_database(CONTAINER_NAME)


if __name__ == "__main__":
    main()
