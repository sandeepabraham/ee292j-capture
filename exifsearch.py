import os
import json
import subprocess
import datetime
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# Set your SerpAPI key from environment variable
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise ValueError("Missing SerpAPI key. Check your environment variables.")

def extract_query_fields(image_path):
    """Extract description/caption/headline from EXIF metadata for smart search queries"""
    try:
        result = subprocess.run(
            [
                "exiftool",
                "-Caption-Abstract",
                "-Headline",
                "-Description",
                "-json",
                image_path
            ],
            capture_output=True, text=True, check=True
        )
        metadata = json.loads(result.stdout)[0]

        # Only search if one of the prioritized fields exists and is non-empty
        for field in ["Caption-Abstract", "Headline", "Description"]:
            value = metadata.get(field)
            if isinstance(value, str) and value.strip():
                return value.strip()

        print(f"[!] Skipping {image_path} — none of Caption-Abstract, Headline, or Description fields found.")
        return None

    except Exception as e:
        print(f"[ERROR] Failed to extract query fields from {image_path}: {e}")
        return None

def search_google_images(query):
    print(f"[INFO] Running image search for: {query}")
    params = {
        "engine": "google_images",
        "q": query,
        "api_key": SERPAPI_KEY
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        if response.status_code != 200:
            raise Exception(f"SerpAPI error: {response.text}")
        data = response.json()

        results = []
        for img in data.get("images_results", []):
            results.append({
                "type": "image",
                "title": img.get("title"),
                "link": img.get("original"),
                "source": img.get("source"),
                "thumbnail": img.get("thumbnail")
            })

        return results
    except Exception as e:
        print(f"[EXCEPTION] Image search failed for query '{query}': {e}")
        return []

def save_results(image_name, results, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{image_name}_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Saved results to {output_path}")

if __name__ == "__main__":
    image_dir = "./input_images"
    output_dir = "./exif_search_results"
    os.makedirs(output_dir, exist_ok=True)

    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    for image_file in image_files:
        image_path = os.path.join(image_dir, image_file)
        query = extract_query_fields(image_path)
        if query:
            results = search_google_images(query)
            save_results(os.path.splitext(image_file)[0], results, output_dir)
