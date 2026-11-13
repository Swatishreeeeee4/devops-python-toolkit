"""Tests use moto: a fake AWS in memory, so no real account or cost."""
import boto3
from moto import mock_aws

from devops_toolkit.aws_audit import audit

R = "ap-southeast-2"


@mock_aws
def test_finds_open_ssh_unused_disk_and_public_bucket():
    ec2 = boto3.client("ec2", region_name=R)
    sg = ec2.create_security_group(GroupName="bad", Description="x")["GroupId"]
    ec2.authorize_security_group_ingress(GroupId=sg, IpProtocol="tcp", FromPort=22, ToPort=22, CidrIp="0.0.0.0/0")
    ec2.create_volume(AvailabilityZone=R + "a", Size=8)
    boto3.client("s3", region_name=R).create_bucket(
        Bucket="open-bucket", CreateBucketConfiguration={"LocationConstraint": R})

    problems = [p for _, _, p in audit(R)]
    assert "SSH open to the internet" in problems
    assert "unattached EBS volume" in problems
    assert "no public access block" in problems


@mock_aws
def test_clean_account_has_no_findings():
    assert audit(R) == []
