# DevOps Python Toolkit

Three small, tested Python tools I use for DevOps automation. Each one is a single short file.

| Tool | What it does | Exit code |
|---|---|---|
| `aws_audit.py` | **boto3**, read-only: finds SSH/RDP open to the internet, unattached EBS volumes, unused Elastic IPs and S3 buckets without a public access block | 1 if anything HIGH (can gate a pipeline) |
| `healthcheck.py` | Checks URLs return 200, with retries (use after a deploy) | 1 if any URL is down |
| `log_report.py` | Summarises an Nginx/Apache access log: status codes, 5xx error rate, top IPs and paths | 0 |

## Use

```bash
pip install -r requirements.txt
AWS_DEFAULT_REGION=us-east-1 python -m devops_toolkit.aws_audit ap-southeast-2
python -m devops_toolkit.healthcheck https://example.com https://example.org/health
python -m devops_toolkit.log_report /var/log/nginx/access.log
```

## Tests and CI

`pytest` runs the AWS tests against **moto** (a fake AWS in memory: no account, no cost), and GitHub Actions
runs `ruff` (lint) and `pytest` on every push.

```bash
pytest -q        # 6 passed
```

## Notes

- Built while learning Python for DevOps (Decoding DevOps course, Section 20). The course's `ostasks.py` used
  `os.system("useradd {}".format(user))`, which allows shell injection; use `subprocess.run([...])` with a list instead.
- `aws login` credentials need `boto3[crt]` and a default region for the token refresh.

## Author

Swatishree Barik · [github.com/Swatishreeeeee4](https://github.com/Swatishreeeeee4)
