#!/usr/bin/env python3

import subprocess
import argparse
import time
import sys
import logging
from pathlib import Path

CONTAINER_NAME = "glyphminer"
IMAGE_NAME = "glyphminer/glyphminer"
CID_FILE = Path("/tmp/glyphminer-container.id")

MYSQL_USER = "glyphminer"
MYSQL_PW = "glyphminer"
MYSQL_DB = "glyphminer"


def setup_logging(logfile):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(logfile),
            logging.StreamHandler(sys.stdout)
        ]
    )


def log(message):
    logging.info(message)


def run(command, check=True, capture_output=False, quiet=False):
    try:
        result = subprocess.run(command, shell=True, check=check,
                                capture_output=capture_output, text=True)
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        if not quiet:
            logging.warning(f"Command failed: {command}")
            if e.stderr:
                logging.warning("stderr: %s", e.stderr.strip())
            elif e.output:
                logging.warning("output: %s", e.output.strip())
            else:
                logging.warning("return code: %s", e.returncode)
        raise


def container_exists(name):
    output = run("docker ps -a --format '{{.Names}}'", capture_output=True)
    return name in output.splitlines()


def container_is_running(name):
    output = run("docker ps --format '{{.Names}}'", capture_output=True)
    return name in output.splitlines()


def stop_and_remove_container(name):
    log(f"Stopping and removing container '{name}'...")
    try:
        run(f"docker stop {name}")
    except subprocess.CalledProcessError:
        pass
    try:
        run(f"docker rm {name}")
    except subprocess.CalledProcessError:
        pass


def truncate_tables(container):
    log("Truncating images and collections tables in running container...")
    query = "TRUNCATE TABLE images; TRUNCATE TABLE collections;"
    run(
        f'docker exec {container} '
        f'mysql -u{MYSQL_USER} -p{MYSQL_PW} -D{MYSQL_DB} '
        f'-e "{query}"'
    )
    log("✅ Tables truncated.")


def release_port_8080():
    log("Checking if port 8080 is already bound...")
    container_ids = run(
        "docker ps --filter 'publish=8080' --format '{{.ID}}'",
        capture_output=True
    ).splitlines()

    if container_ids:
        log(f"⚠️  Port 8080 is in use by {len(container_ids)} container(s). Stopping and removing them...")
        for cid in container_ids:
            try:
                run(f"docker stop {cid}")
                run(f"docker rm {cid}")
            except subprocess.CalledProcessError as e:
                log(f"❌ Failed to stop/remove container {cid}: {e}")
        log("✅ Port 8080 has been freed.")
    else:
        log("✅ Port 8080 is free.")


def start_container(name):
    log("Starting new container...")
    container_id = run(
        f"docker run -d -p 8080:80 --name {name} {IMAGE_NAME}",
        capture_output=True
    )
    log(f"Container started with ID: {container_id}")
    CID_FILE.write_text(container_id + "\n")
    log(f"Saved container ID to {CID_FILE}")
    return container_id


def wait_for_mysql(container, retries=10, delay=2):
    print("Waiting for MySQL to become ready...", end="", flush=True)
    for _ in range(retries):
        try:
            run(
                f'docker exec {container} '
                f'mysql -u{MYSQL_USER} -p{MYSQL_PW} -D{MYSQL_DB} -e "SELECT 1;"',
                capture_output=True,
                quiet=True
            )
            print(" ready.")
            return True
        except subprocess.CalledProcessError:
            print(".", end="", flush=True)
            time.sleep(delay)
    print("\n❌ MySQL did not become ready in time.")
    log("❌ MySQL did not become ready in time.")
    return False


def check_database(container):
    if not wait_for_mysql(container):
        return

    log("Checking database contents...")
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
                log(f"✅ {table}: {lines[1]} rows")
            else:
                log(f"⚠️  Unexpected response for table {table}: {count}")
        except subprocess.CalledProcessError as e:
            log(f"❌ Error checking table {table}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Restart Glyphminer Docker container.")
    parser.add_argument("--reset-db", action="store_true",
                        help="Also remove the Docker image to wipe the database")
    parser.add_argument("--running-action", choices=["kill", "clean"], default="kill",
                        help="What to do if the container is already running (default: kill)")
    parser.add_argument("--logfile", default="restart-server_docker.log",
                        help="Path to logfile (default: restart-server_docker.log)")
    args = parser.parse_args()

    setup_logging(args.logfile)

    if container_is_running(CONTAINER_NAME):
        log(f"Container '{CONTAINER_NAME}' is already running.")
        if args.running_action == "kill":
            stop_and_remove_container(CONTAINER_NAME)
            release_port_8080()
            container_id = start_container(CONTAINER_NAME)
            check_database(CONTAINER_NAME)
        elif args.running_action == "clean":
            truncate_tables(CONTAINER_NAME)
            check_database(CONTAINER_NAME)
        return

    if container_exists(CONTAINER_NAME):
        stop_and_remove_container(CONTAINER_NAME)

    if args.reset_db:
        run(f"docker rmi {IMAGE_NAME}")

    release_port_8080()
    container_id = start_container(CONTAINER_NAME)
    check_database(CONTAINER_NAME)


if __name__ == "__main__":
    main()
