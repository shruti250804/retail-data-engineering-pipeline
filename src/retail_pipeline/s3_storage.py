import os
from pathlib import Path

def upload_file_to_s3(local_path, bucket=None, key=None):
    """Upload a local file to S3 using credentials from the AWS SDK/CLI profile."""
    import boto3

    bucket = bucket or os.getenv("S3_BUCKET")
    if not bucket:
        raise ValueError("Set S3_BUCKET before uploading.")
    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(local_path)
    key = key or f"{os.getenv('S3_PREFIX', 'retail-pipeline/processed/').rstrip('/')}/{local_path.name}"
    boto3.client("s3").upload_file(str(local_path), bucket, key)
    return f"s3://{bucket}/{key}"
