import os
import json
import requests
from urllib.parse import urlparse

RESULTS_FOLDER = "./exif_search_results"
DOWNLOAD_FOLDER = "./downloaded_media/audio_video"
VALID_MEDIA_TYPES = ["audio", "video"]

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def sanitize_filename(name):
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

def get_extension(response, fallback_ext="bin"):
    content_type = response.headers.get("Content-Type", "").lower()
    if "video/mp4" in content_type:
        return "mp4"
    elif "video/webm" in content_type:
        return "webm"
    elif "audio/mpeg" in content_type:
        return "mp3"
    elif "audio/ogg" in content_type:
        return "ogg"
    elif "audio/wav" in content_type:
        return "wav"
    return fallback_ext

def download_media_item(item, base_name):
    url = item.get("link")
    if not url:
        return

    safe_title = sanitize_filename(item.get("title") or "untitled")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        with requests.get(url, headers=headers, stream=True, timeout=15) as r:
            if r.status_code == 200:
                ext = get_extension(r)
                filename = f"{base_name}_{safe_title[:40]}.{ext}"
                filepath = os.path.join(DOWNLOAD_FOLDER, filename)
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"[✓] Downloaded: {filename}")
            else:
                print(f"[✗] Failed to fetch {url} (status {r.status_code})")
    except Exception as e:
        print(f"[✗] Error downloading {url}: {e}")

def main():
    for fname in os.listdir(RESULTS_FOLDER):
        if not fname.endswith("av.json"):
            continue

        result_path = os.path.join(RESULTS_FOLDER, fname)
        with open(result_path, "r") as f:
            try:
                data = json.load(f)
                results = data.get("results", [])
                base_name = fname.replace("_results.json", "").replace(".json", "")

                for item in results:
                    if item.get("type") in VALID_MEDIA_TYPES:
                        download_media_item(item, base_name)
            except Exception as e:
                print(f"[✗] Could not read {fname}: {e}")

if __name__ == "__main__":
    main()
