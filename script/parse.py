import requests
import os
import tempfile
import re
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from pytz import timezone
from typing import Optional
from urllib.parse import urlparse

import boto3
import pandas as pd
import polars as pl
from botocore import UNSIGNED
from botocore.client import Config

from config import (
    PARQUERT_DIR,
    BASE_URL,
    METADATA,
    COLUMNS,
    S3_BUCKET_NAME,
    S3_REGION_NAME,
    ELECTRONIC_FEC_PREFIX,
)


s3_client = boto3.client(
    "s3", region_name=S3_REGION_NAME, config=Config(signature_version=UNSIGNED)
)


def download_zip(
    url: str, save_path: Optional[str] = None, use_temp: bool = True
) -> str:
    """
    Download a ZIP file from a given URL and save it to disk.

    Args:
        url (str): The URL of the ZIP file to download
        save_path (str, optional): The path where the ZIP file should be saved.
            If not provided and use_temp is False, the filename from the URL will be used.
        use_temp (bool): If True, save the file to a temporary location

    Returns:
        str: The path to the downloaded file

    Raises:
        requests.exceptions.RequestException: If there's an error downloading the file
        IOError: If there's an error saving the file
        ValueError: If the URL or save path is invalid
    """
    try:
        # Validate URL
        if not url.strip():
            raise ValueError("URL cannot be empty")

        # Make HTTP request with stream=True to handle large files
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Check if the content type is zip
        content_type = response.headers.get("content-type", "")
        if "application/zip" not in content_type.lower():
            print(
                f"Warning: Content-Type '{content_type}' does not indicate a ZIP file"
            )

        if use_temp:
            # Create temporary file with .zip extension
            temp_fd, save_path = tempfile.mkstemp(suffix=".zip")
            os.close(temp_fd)  # Close file descriptor
        elif save_path is None:
            # Extract filename from URL
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = "downloaded.zip"
            save_path = filename

        if not use_temp:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

        # Save the file
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return save_path

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error downloading file: {str(e)}")
    except IOError as e:
        raise IOError(f"Error saving file: {str(e)}")


def extract_zip(
    zip_path: str, extract_dir: Optional[str] = None, delete_zip: bool = True
) -> str:
    """
    Extract a ZIP file to a specified directory, moving files from the root folder
    directly into the extract path.

    Args:
        zip_path (str): Path to the ZIP file
        extract_dir (str, optional): Directory where files should be extracted.
            If not provided, a temporary directory will be created.
        delete_zip (bool): Whether to delete the ZIP file after extraction

    Returns:
        str: Path to the directory containing extracted files

    Raises:
        zipfile.BadZipFile: If the file is not a valid ZIP file
        IOError: If there's an error during extraction
        ValueError: If malicious paths are detected in the ZIP
    """
    try:
        if extract_dir is None:
            # Create a temporary directory for extraction
            extract_dir = tempfile.mkdtemp()
        else:
            # Create extraction directory if it doesn't exist
            os.makedirs(extract_dir, exist_ok=True)

        # Create a temporary directory for initial extraction
        temp_extract_dir = tempfile.mkdtemp()

        try:
            # Extract the ZIP file to temporary location
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Check for malicious paths (path traversal attacks)
                for zip_info in zip_ref.filelist:
                    if os.path.isabs(zip_info.filename) or ".." in zip_info.filename:
                        raise ValueError(
                            f"Malicious path detected in ZIP: {zip_info.filename}"
                        )
                # Extract all files to temporary location
                zip_ref.extractall(temp_extract_dir)

            # Get the contents of the temporary directory
            temp_contents = os.listdir(temp_extract_dir)

            if len(temp_contents) == 1 and os.path.isdir(
                os.path.join(temp_extract_dir, temp_contents[0])
            ):
                # If there's a single folder, move its contents to extract_dir
                root_folder = os.path.join(temp_extract_dir, temp_contents[0])
                for item in os.listdir(root_folder):
                    source = os.path.join(root_folder, item)
                    destination = os.path.join(extract_dir, item)

                    # If destination exists, remove it first
                    if os.path.exists(destination):
                        if os.path.isdir(destination):
                            shutil.rmtree(destination)
                        else:
                            os.remove(destination)

                    # Move the item to the final destination
                    shutil.move(source, destination)
            else:
                # If it's not a single folder, move everything directly
                for item in temp_contents:
                    source = os.path.join(temp_extract_dir, item)
                    destination = os.path.join(extract_dir, item)

                    # If destination exists, remove it first
                    if os.path.exists(destination):
                        if os.path.isdir(destination):
                            shutil.rmtree(destination)
                        else:
                            os.remove(destination)

                    # Move the item to the final destination
                    shutil.move(source, destination)

        finally:
            # Clean up temporary directory
            if os.path.exists(temp_extract_dir):
                shutil.rmtree(temp_extract_dir)

        # Delete the ZIP file if requested
        if delete_zip:
            os.remove(zip_path)

        return extract_dir

    except zipfile.BadZipFile as e:
        raise zipfile.BadZipFile(f"Invalid ZIP file: {str(e)}")
    except IOError as e:
        raise IOError(f"Error during extraction: {str(e)}")


def list_files_by_type(directory, file_type):
    """
    List full paths of all files with a specific extension in a given directory.

    Args:
        directory (str): The directory path to search
        file_type (str): File extension to search for (e.g. 'txt', 'pdf', 'csv')

    Returns:
        list: List of full paths to files with the specified extension
    """
    try:
        # Ensure file_type starts with a period
        extension = f".{file_type.lower().strip('.')}"

        matching_files = []
        for file in os.listdir(directory):
            if file.lower().endswith(extension):
                matching_files.append(os.path.join(directory, file))
        return matching_files
    except Exception as e:
        print(f"Error accessing directory: {str(e)}")
        return []


def save_in_parquet(input_path, column_names, output_path):
    """
    Read a text file as CSV with specified columns and save as parquet.
    All columns are treated as strings.

    Args:
        input_path (str): Path to the input text file
        column_names (list): List of column names
        output_path (str): Path where parquet file should be saved

    Returns:
        bool: True if conversion successful, False otherwise
    """
    try:
        # Read CSV file with specified columns
        df = pd.read_csv(
            input_path,
            names=column_names,
            dtype=str,  # Treat all columns as strings
            skip_blank_lines=True,
        )

        # Save as parquet
        df.to_parquet(output_path, index=False)
        return True

    except Exception as e:
        print(f"Error converting file: {str(e)}")
        return False


def file_exists_and_complete(local_path, expected_size):
    """
    Check if file exists and has the expected size
    """
    if not os.path.exists(local_path):
        return False
    return os.path.getsize(local_path) == expected_size


def download_s3_file(bucket_name, object_key, local_path, expected_size):
    """
    Download a file from S3 GovCloud bucket if it doesn't exist locally
    """
    try:
        if file_exists_and_complete(local_path, expected_size):
            print(f"Skipping {object_key} - file already exists")
            return True

        print(f"Downloading {object_key} to {local_path}")
        s3_client.download_file(bucket_name, object_key, local_path)

        # Verify the downloaded file size
        if file_exists_and_complete(local_path, expected_size):
            print(f"Successfully downloaded {object_key}")
            return True
        else:
            print(f"Error: Downloaded file size mismatch for {object_key}")
            return False

    except Exception as e:
        print(f"Error downloading file: {e}")
        return False


def get_date_from_filename(filename):
    """
    Extract date from filename like '<date>.zip'
    Example: '20241029.zip' returns datetime(2024, 10, 29)
    """
    try:
        # Use regex to match the date pattern
        match = re.match(r"(\d{8})\.zip$", filename)
        if match:
            date_str = match.group(1)
            return datetime.strptime(date_str, "%Y%m%d")
        return None
    except ValueError:
        return None


def list_and_download_files_after_date(
    bucket_name, start_date, prefix="", download_dir="downloads"
):
    """
    List and download all .zip files with date-based names after the specified start date,
    skipping files that already exist locally

    Args:
        bucket_name (str): Name of the S3 bucket
        start_date (datetime or str): Starting date to filter files (format: YYYYMMDD)
        prefix (str): Prefix to filter objects (folder path)
        download_dir (str): Local directory to save downloaded files
    """
    try:
        # Ensure download directory exists
        os.makedirs(download_dir, exist_ok=True)

        # Convert start_date to datetime if it's string
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y%m%d")

        print(f"Looking for files after {start_date.strftime('%Y-%m-%d')}...")

        paginator = s3_client.get_paginator("list_objects_v2")
        params = {"Bucket": bucket_name}
        if prefix:
            params["Prefix"] = prefix

        files_to_process = []
        total_size = 0

        # Collect all matching files
        for page in paginator.paginate(**params):
            if "Contents" in page:
                for obj in page["Contents"]:
                    filename = os.path.basename(obj["Key"])

                    # Check if file matches '<date>.zip' pattern
                    if not filename.endswith(".zip"):
                        continue

                    file_date = get_date_from_filename(filename)
                    if file_date and file_date >= start_date:
                        local_path = os.path.join(download_dir, filename)

                        files_to_process.append(
                            {
                                "key": obj["Key"],
                                "date": file_date,
                                "size": obj["Size"],
                                "local_path": local_path,
                                "exists": file_exists_and_complete(
                                    local_path, obj["Size"]
                                ),
                            }
                        )

                        if not file_exists_and_complete(local_path, obj["Size"]):
                            total_size += obj["Size"]

        # Sort files by date
        files_to_process.sort(key=lambda x: x["date"])

        if not files_to_process:
            print("No matching files found.")
            return []

        # Count files that need to be downloaded
        files_to_download = [f for f in files_to_process if not f["exists"]]

        print(f"\nFound {len(files_to_process)} matching files:")
        print(f"- {len(files_to_download)} files need to be downloaded")
        print(
            f"- {len(files_to_process) - len(files_to_download)} files already exist locally"
        )

        if files_to_download:
            print(
                f"\nTotal download size: {total_size:,} bytes ({total_size / (1024*1024*1024):.2f} GB)"
            )
            print("\nFiles to download:")
            for file in files_to_download:
                print(f"- {file['key']}")
                print(f"  Date: {file['date'].strftime('%Y-%m-%d')}")
                print(f"  Size: {file['size']:,} bytes")

            # Confirm download if size is significant
            total_gb = total_size / (1024 * 1024 * 1024)
            if total_gb > 1:
                response = input(
                    f"\nThis will download {total_gb:.2f} GB of data. Continue? (y/n): "
                )
                if response.lower() != "y":
                    print("Download cancelled.")
                    return []
        else:
            print("\nAll files already exist locally. No downloads needed.")
            return [f["local_path"] for f in files_to_process]

        # Download files
        print("\nStarting downloads...")
        downloaded_files = []
        skipped_files = []

        for file in files_to_process:
            if file["exists"]:
                skipped_files.append(file["local_path"])
                continue

            if download_s3_file(
                bucket_name, file["key"], file["local_path"], file["size"]
            ):
                downloaded_files.append(file["local_path"])

        print("\nDownload summary:")
        print(f"- Total files processed: {len(files_to_process)}")
        print(f"- Files skipped (already existed): {len(skipped_files)}")
        print(f"- Files downloaded: {len(downloaded_files)}")
        print(f"- Download directory: {os.path.abspath(download_dir)}")

        return downloaded_files + skipped_files

    except Exception as e:
        print(f"Error processing files: {e}")
        return []


def parse_statements_and_summary():
    for metadata in METADATA:
        year = metadata["year"]
        category = metadata["category"]
        url = f'{BASE_URL}{metadata["remainder"]}'

        # Download and extract to temp location
        zip_path = download_zip(url, use_temp=True)
        extracted_path = extract_zip(zip_path, category)
        txt_files = list_files_by_type(extracted_path, "txt")

        # Convert and save in Parquet
        columns = COLUMNS[category]
        parquet_file = f"{PARQUERT_DIR}/{category}_{year}.parquet"
        save_in_parquet(txt_files[0], columns, parquet_file)
        print(f"Successfully save {parquet_file}")

        # Clean up temporary files when done
        shutil.rmtree(extracted_path)


def parse_electronic_filed_reports(start_date: str = None):
    if start_date is None:
        tz = timezone("EST")
        start_date = datetime.now(tz).strftime("%Y%m%d")

    print(f"Parse Electronic Filed Reports since {start_date}")

    downloaded_files = list_and_download_files_after_date(
        bucket_name=S3_BUCKET_NAME,
        start_date=start_date,
        prefix=ELECTRONIC_FEC_PREFIX,
        download_dir="downloads/electronic_zip",
    )

    extract_dir = "downloads/electronic_fec"
    csv_dir = "downloads/electronic_fec_csv"
    parquet_dir = "downloads/electronic_fec_parquet"
    os.makedirs(parquet_dir, exist_ok=True)
    for zip_file in downloaded_files:
        extract_zip(zip_path=zip_file, extract_dir=extract_dir, delete_zip=False)

        fec_files = list_files_by_type(extract_dir, "fec")
        csv_files_by_form_type = dict()
        parquet_dfs_by_form_type = dict()
        for fec_file in fec_files:
            try:
                fec_id = Path(fec_file).stem
                output_dir = f"{csv_dir}/{fec_id}"

                if not Path(output_dir).exists():
                    print(f"Parsing {fec_file}")
                    subprocess.run(["fastfec", fec_file, csv_dir])

                csv_files = list_files_by_type(output_dir, "csv")
                for csv_file in csv_files:
                    if Path(csv_file).stat().st_size == 0:
                        continue

                    form_type = Path(csv_file).stem
                    if form_type not in csv_files_by_form_type:
                        csv_files_by_form_type[form_type] = list()
                    csv_files_by_form_type[form_type].append(csv_file)

            except Exception as e:
                print(f"Error parsing {fec_file}: {e}")
                pass

        print(f"All FEC files in {zip_file} are parsed")
        for form_type, csv_files in csv_files_by_form_type.items():
            csv_df = pl.concat(
                [
                    pl.read_csv(
                        csv_file, infer_schema=False, truncate_ragged_lines=True
                    )
                    for csv_file in csv_files
                ]
            )

            if form_type not in parquet_dfs_by_form_type:
                parquet_file = f"{parquet_dir}/{form_type}.parquet"
                if Path(parquet_file).exists():
                    parquet_dfs_by_form_type[form_type] = pl.read_parquet(parquet_file)
                    parquet_dfs_by_form_type[form_type] = pl.concat([parquet_dfs_by_form_type[form_type], csv_df])
                else:
                    parquet_dfs_by_form_type[form_type] = csv_df
            else:
                parquet_dfs_by_form_type[form_type] = pl.concat([parquet_dfs_by_form_type[form_type], csv_df])

        print("Start updating Parquet files")
        for form_type, df in parquet_dfs_by_form_type.items():
            parquet_file = f"{parquet_dir}/{form_type}.parquet"
            df.write_parquet(parquet_file)
            print(f"Update {parquet_file}")


os.makedirs(PARQUERT_DIR, exist_ok=True)

parse_electronic_filed_reports("20241026")
