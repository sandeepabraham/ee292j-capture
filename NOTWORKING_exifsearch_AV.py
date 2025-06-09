import os
import json
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv
import exiftool

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SEARCH_ENGINE = os.getenv("SEARCH_ENGINE", "google")  # Can be "google" or "youtube"
INPUT_FOLDER = "./input_images"
OUTPUT_FOLDER = "./exif_search_results"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

PRIORITY_FIELDS = [
    "Caption-Abstract",
    "Headline",
    "Description",
    "ImageDescription",
    "XPTitle",
    "XPSubject"
]

def extract_priority_metadata_fields(image_path):
    try:
        with exiftool.ExifTool() as et:
            metadata = et.execute_json(image_path)[0]
        normalized_metadata = {k.split(":")[-1]: v for k, v in metadata.items()}
        for field in PRIORITY_FIELDS:
            value = normalized_metadata.get(field)
            if value:
                if isinstance(value, bytes):
                    value = value.decode("utf-16-le", errors="ignore")
                elif isinstance(value, list):
                    value = " ".join(map(str, value))
                return str(value).strip()
        return None
    except Exception as e:
        print(f"[WARN] Failed to read EXIF from {image_path}: {e}")
        return None

def run_search(query, engine="google"):
    if not SERPAPI_KEY:
        raise ValueError("Missing SerpAPI key. Check your environment variables.")

    params = {
        "q": query,
        "api_key": SERPAPI_KEY
    }

    if engine == "google":
        params["engine"] = "google"
    elif engine == "youtube":
        params["engine"] = "youtube"
        #params["type"] = "video"
    else:
        raise ValueError(f"Unsupported search engine: {engine}")

    search = GoogleSearch(params)
    result = search.get_dict()

    media_results = []
    if engine == "google":
        for entry in result.get("inline_videos", []) + result.get("video_results", []):
            media_results.append({
                "type": "video",
                "title": entry.get("title"),
                "link": entry.get("link")
            })
        for entry in result.get("audio_results", []):
            media_results.append({
                "type": "audio",
                "title": entry.get("title"),
                "link": entry.get("link")
            })
    elif engine == "youtube":
        for entry in result.get("video_results", []):
            media_results.append({
                "type": "video",
                "title": entry.get("title"),
                "link": entry.get("link")
            })

    return media_results

def main():
    for fname in os.listdir(INPUT_FOLDER):
        if not fname.lower().endswith((".jpg", ".jpeg")):
            continue

        image_path = os.path.join(INPUT_FOLDER, fname)
        print(f"[INFO] Processing {fname}")

        query = extract_priority_metadata_fields(image_path)
        if not query:
            print(f"[SKIP] No valid EXIF text fields in {fname}")
            continue

        try:
            results = run_search(query, SEARCH_ENGINE)
            out_fname = os.path.join(OUTPUT_FOLDER, f"{fname}_av.json")
            with open(out_fname, "w") as f:
                json.dump({"query": query, "results": results}, f, indent=2)
            print(f"[✓] Saved AV results to {out_fname}")
        except Exception as e:
            print(f"[ERROR] Failed search for {fname}: {e}")

if __name__ == "__main__":
    main()
