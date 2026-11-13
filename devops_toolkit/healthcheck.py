"""Check that URLs answer 200, retrying a few times (use it right after a deploy).

Usage: python -m devops_toolkit.healthcheck https://site1 https://site2
Exit code 1 if any URL is down.
"""
import sys
import time
import urllib.request


def is_up(url, retries=3, wait=2):
    for _ in range(retries):
        try:
            return urllib.request.urlopen(url, timeout=5).status == 200
        except OSError:  # connection refused, timeout or HTTP error: wait and try again
            time.sleep(wait)
    return False


if __name__ == "__main__":
    down = [u for u in sys.argv[1:] if not is_up(u)]
    print("DOWN:", down if down else "none")
    sys.exit(1 if down else 0)
