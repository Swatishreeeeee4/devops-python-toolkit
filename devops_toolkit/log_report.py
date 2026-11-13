"""Summarise a web server access log (Apache/Nginx "combined" format).

Prints requests per status class, the 5xx error rate, top client IPs and top paths.
Usage:  python -m devops_toolkit.log_report /var/log/nginx/access.log [--top 5] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field

LINE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[[^\]]+\] "(?P<method>[A-Z]+) (?P<path>\S+)[^"]*" (?P<status>\d{3}) '
)


@dataclass
class Report:
    total: int = 0
    unparsed: int = 0
    by_status_class: dict = field(default_factory=dict)
    error_rate_5xx: float = 0.0
    top_ips: list = field(default_factory=list)
    top_paths: list = field(default_factory=list)


def analyse(lines, top: int = 5) -> Report:
    classes, ips, paths = Counter(), Counter(), Counter()
    r = Report()
    for line in lines:
        m = LINE.match(line)
        if not m:
            r.unparsed += 1
            continue
        r.total += 1
        classes[m["status"][0] + "xx"] += 1
        ips[m["ip"]] += 1
        paths[m["path"].split("?")[0]] += 1
    r.by_status_class = dict(sorted(classes.items()))
    r.error_rate_5xx = round(100 * classes["5xx"] / r.total, 2) if r.total else 0.0
    r.top_ips, r.top_paths = ips.most_common(top), paths.most_common(top)
    return r


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("logfile")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    with open(args.logfile, encoding="utf-8", errors="replace") as fh:
        rep = analyse(fh, args.top)
    if args.json:
        print(json.dumps(asdict(rep), indent=2))
        return 0
    print(f"Requests: {rep.total}  (unparsed lines: {rep.unparsed})")
    print("By status:", ", ".join(f"{k}={v}" for k, v in rep.by_status_class.items()))
    print(f"5xx error rate: {rep.error_rate_5xx}%")
    print("Top IPs:  ", ", ".join(f"{ip} ({n})" for ip, n in rep.top_ips))
    print("Top paths:", ", ".join(f"{p} ({n})" for p, n in rep.top_paths))
    return 0


if __name__ == "__main__":
    sys.exit(main())
