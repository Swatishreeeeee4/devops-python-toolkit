"""Read-only AWS audit: finds security risks and wasted money in one region.

Usage: python -m devops_toolkit.aws_audit ap-southeast-2
Exit code 1 if anything HIGH is found (so a pipeline can stop).
"""
import sys

import boto3
from botocore.exceptions import ClientError


def audit(region):
    ec2 = boto3.client("ec2", region_name=region)
    s3 = boto3.client("s3", region_name=region)
    found = []  # list of (severity, resource, problem)

    # 1. SSH/RDP open to the whole internet
    for sg in ec2.describe_security_groups()["SecurityGroups"]:
        for rule in sg["IpPermissions"]:
            world = any(r["CidrIp"] == "0.0.0.0/0" for r in rule.get("IpRanges", []))
            for port, name in [(22, "SSH"), (3389, "RDP")]:
                all_ports = rule["IpProtocol"] == "-1"
                in_range = rule.get("FromPort", 0) <= port <= rule.get("ToPort", 0)
                if world and (all_ports or in_range):
                    found.append(("HIGH", sg["GroupId"], f"{name} open to the internet"))

    # 2. Disks nobody uses, 3. IPs nobody uses (both still cost money)
    for v in ec2.describe_volumes(Filters=[{"Name": "status", "Values": ["available"]}])["Volumes"]:
        found.append(("MEDIUM", v["VolumeId"], "unattached EBS volume"))
    for ip in ec2.describe_addresses()["Addresses"]:
        if "AssociationId" not in ip:
            found.append(("MEDIUM", ip["PublicIp"], "unused Elastic IP"))

    # 4. S3 buckets that are not fully blocked from public access
    for b in s3.list_buckets()["Buckets"]:
        try:
            block = s3.get_public_access_block(Bucket=b["Name"])["PublicAccessBlockConfiguration"]
            if not all(block.values()):
                found.append(("HIGH", b["Name"], "public access block only partly on"))
        except ClientError:
            found.append(("HIGH", b["Name"], "no public access block"))

    return found


if __name__ == "__main__":
    results = audit(sys.argv[1])
    for severity, resource, problem in results:
        print(f"{severity:<7} {resource:<25} {problem}")
    print(f"{len(results)} finding(s)")
    sys.exit(1 if any(r[0] == "HIGH" for r in results) else 0)
