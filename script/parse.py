import requests
import os
import tempfile
import shutil
import zipfile
from urllib.parse import urlparse
from typing import Optional

import pandas as pd

from config import PARQUERT_DIR, BASE_URL, METADATA, COLUMNS


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
    zip_path: str, extract_path: Optional[str] = None, delete_zip: bool = True
) -> str:
    """
    Extract a ZIP file to a specified directory.

    Args:
        zip_path (str): Path to the ZIP file
        extract_path (str, optional): Directory where files should be extracted.
            If not provided, a temporary directory will be created.
        delete_zip (bool): Whether to delete the ZIP file after extraction

    Returns:
        str: Path to the directory containing extracted files

    Raises:
        zipfile.BadZipFile: If the file is not a valid ZIP file
        IOError: If there's an error during extraction
    """
    try:
        if extract_path is None:
            # Create a temporary directory for extraction
            extract_path = tempfile.mkdtemp()
        else:
            # Create extraction directory if it doesn't exist
            os.makedirs(extract_path, exist_ok=True)

        # Extract the ZIP file
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # Check for malicious paths (path traversal attacks)
            for zip_info in zip_ref.filelist:
                if os.path.isabs(zip_info.filename) or ".." in zip_info.filename:
                    raise ValueError(
                        f"Malicious path detected in ZIP: {zip_info.filename}"
                    )
            # Extract all files
            zip_ref.extractall(extract_path)

        # Delete the ZIP file if requested
        if delete_zip:
            os.remove(zip_path)

        return extract_path

    except zipfile.BadZipFile as e:
        raise zipfile.BadZipFile(f"Invalid ZIP file: {str(e)}")
    except IOError as e:
        raise IOError(f"Error during extraction: {str(e)}")


def list_txt_files(directory):
    """
    List full paths of all .txt files in a given directory.

    Args:
        directory (str): The directory path to search

    Returns:
        list: List of full paths to .txt files
    """
    try:
        txt_files = []
        for file in os.listdir(directory):
            if file.endswith(".txt"):
                txt_files.append(os.path.join(directory, file))
        return txt_files
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


os.makedirs(PARQUERT_DIR, exist_ok=True)

for metadata in METADATA:
    year = metadata["year"]
    category = metadata["category"]
    url = f'{BASE_URL}{metadata["remainder"]}'

    # Download and extract to temp location
    zip_path = download_zip(url, use_temp=True)
    extracted_path = extract_zip(zip_path, category)
    txt_files = list_txt_files(extracted_path)

    # Convert and save in Parquet
    columns = COLUMNS[category]
    parquet_file = f"{PARQUERT_DIR}/{category}_{year}.parquet"
    save_in_parquet(txt_files[0], columns, parquet_file)
    print(f"Successfully save {parquet_file}")

    # Clean up temporary files when done
    shutil.rmtree(extracted_path)
