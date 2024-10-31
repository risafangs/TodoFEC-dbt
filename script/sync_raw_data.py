import os
from pathlib import Path
from typing import Optional, List

import boto3
from botocore import UNSIGNED
from botocore.client import Config

from config import (
    DATARECCE_TODOFEC_S3_BUCKET_NAME,
    DATARECCE_TODOFEC_S3_REGION_NAME,
    RAW_DATA_DIR,
)


# Initialize S3 client
s3_client = boto3.client(
    "s3",
    region_name=DATARECCE_TODOFEC_S3_REGION_NAME,
    config=Config(signature_version=UNSIGNED),
)


def sync_s3_bucket(
    bucket_name: str,
    local_dir: str,
    prefix: str = "",
    files: Optional[List[str]] = None,
    exclude_extensions: Optional[list[str]] = None,
) -> tuple[int, list[str]]:
    """
    Syncs contents of a public S3 bucket to a local directory.

    Args:
        bucket_name: Name of the S3 bucket
        local_dir: Local directory path to sync files to
        prefix: Optional prefix to filter S3 objects (default: "")
        files: Optional list of specific files to download (default: None)
        exclude_extensions: List of file extensions to exclude (default: None)

    Returns:
        tuple: (Number of files synced, List of errors if any)

    Raises:
        ClientError: If bucket access fails
        OSError: If local directory operations fail
    """
    # Create local directory if it doesn't exist
    Path(local_dir).mkdir(parents=True, exist_ok=True)

    files_synced = 0
    errors = []

    try:
        # If specific files are provided, download them directly
        if files:
            for key in files:
                if exclude_extensions and any(
                    key.endswith(ext) for ext in exclude_extensions
                ):
                    continue

                local_path = os.path.join(local_dir, key)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                try:
                    s3_client.download_file(bucket_name, key, local_path)
                    print(f"Downloaded: {key}")
                    files_synced += 1
                except Exception as e:
                    error_msg = f"Failed to download {key}: {str(e)}"
                    print(error_msg)
                    errors.append(error_msg)
        else:
            # Otherwise, try to list and download all objects with the given prefix
            paginator = s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

            for page in page_iterator:
                if "Contents" not in page:
                    continue

                for obj in page["Contents"]:
                    key = obj["Key"]

                    if exclude_extensions and any(
                        key.endswith(ext) for ext in exclude_extensions
                    ):
                        continue

                    local_path = os.path.join(local_dir, key)
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)

                    try:
                        s3_client.download_file(bucket_name, key, local_path)
                        print(f"Downloaded: {key}")
                        files_synced += 1
                    except Exception as e:
                        error_msg = f"Failed to download {key}: {str(e)}"
                        print(error_msg)
                        errors.append(error_msg)

        return files_synced, errors

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        return 0, [error_msg]


if __name__ == "__main__":
    files_synced, errors = sync_s3_bucket(
        bucket_name=DATARECCE_TODOFEC_S3_BUCKET_NAME, local_dir=RAW_DATA_DIR
    )

    print(f"\nSynced {files_synced} files")
    if errors:
        print("Errors encountered:")
        for error in errors:
            print(f"- {error}")
