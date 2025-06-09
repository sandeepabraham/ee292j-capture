import os
import json
import requests
import shutil
import subprocess
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
from datetime import datetime

# Helper: Extract EXIF date and location from image

def extract_exif_info(image_path):
    try:
        result = subprocess.run(
            [
                "exiftool",
                "-DateTimeOriginal",
                "-CreateDate",
                "-City",
                "-Country",
                "-json",
                image_path
            ],
            capture_output=True, text=True, check=True
        )
        metadata = json.loads(result.stdout)[0]

        date = metadata.get("DateTimeOriginal") or metadata.get("CreateDate")
        location_parts = [metadata.get("City"), metadata.get("Country")]
        location = "_".join(filter(None, location_parts))

        if date:
            date = date.replace(":", "-").replace(" ", "T")  # Format for filenames

        return date, location
    except Exception as e:
        print(f"[WARN] Couldn't extract EXIF metadata from {image_path}: {e}")
        return None, None

# Helper: Build filename from result and EXIF metadata

def build_filename(base_name, index, ext, date=None, location=None):
    parts = [base_name, str(index)]
    if location:
        parts.append(location.replace(" ", "_"))
    if date:
        parts.append(date)
    return "_".join(parts) + ext

# Download image from URL

def download_image(url, save_path):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}  # Some sites block Python requests
        r = requests.get(url, headers=headers, stream=True, timeout=15)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            print(f"[✓] Saved {save_path}")
        else:
            print(f"[WARN] Failed to fetch {url} (status {r.status_code})")
    except Exception as e:
        print(f"[ERROR] Could not download {url}: {e}")

# Main logic

def download_from_results_file(results_file):
    with open(results_file, "r") as f:
        results = json.load(f)

    base_name = os.path.splitext(os.path.basename(results_file))[0].replace("_results", "")
    input_image_path = os.path.join("./input_images", base_name + ".jpg")
    if not os.path.exists(input_image_path):
        input_image_path = os.path.join("./input_images", base_name + ".jpeg")

    date_str, location_str = extract_exif_info(input_image_path)

    output_dir = "./downloaded_images"
    os.makedirs(output_dir, exist_ok=True)

    for i, item in enumerate(results):
        if item.get("type") != "image":
            continue
        url = item.get("link")
        if not url:
            continue

        parsed_url = urlparse(url)
        ext = os.path.splitext(parsed_url.path)[1] or ".jpg"
        filename = build_filename(base_name, i+1, ext, date=date_str, location=location_str)
        save_path = os.path.join(output_dir, filename)
        download_image(url, save_path)

if __name__ == "__main__":
    results_dir = "./exif_search_results"
    results_files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if f.endswith(".json")]

    for results_file in results_files:
        download_from_results_file(results_file)
