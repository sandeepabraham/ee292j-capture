import os
import json
import requests
import base64
import subprocess
from dotenv import load_dotenv

load_dotenv()

# API keys (insert yours into the .env file)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
TINEYE_API_KEY = os.getenv("TINEYE_API_KEY")  # Optional, if/when available
BING_API_KEY = os.getenv("BING_API_KEY")  # Optional, if/when available

INPUT_IMAGE_DIR = "./input_images"
OUTPUT_DIR = "./reverse_image_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def search_google_reverse(image_path):
    if not SERPAPI_KEY:
        print("[!] Missing SerpAPI key. Skipping Google reverse image search.")
        return []
    try:
        print(f"[INFO] Submitting to Google Reverse Image Search: {image_path}")
        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")

        payload = {
            "engine": "google_reverse_image",
            "image_content": encoded_image,
            "api_key": SERPAPI_KEY
        }
        response = requests.post("https://serpapi.com/search", json=payload)
        if response.status_code != 200:
            raise Exception(f"SerpAPI error: {response.text}")

        data = response.json()
        results = []
        for result in data.get("image_results", []):
            results.append({
                "title": result.get("title"),
                "link": result.get("link"),
                "source": result.get("source")
            })
        return results

    except Exception as e:
        print(f"[ERROR] Google reverse image search failed for {image_path}: {e}")
        return []

def search_tineye_stub(image_path):
    if not TINEYE_API_KEY:
        print(f"[!] TinEye API key not provided. Skipping TinEye search for {image_path}.")
        return []
    print(f"[TODO] TinEye reverse image search would be implemented here for {image_path}.")
    # Placeholder for when TinEye API access is available
    return []

def search_bing_visual(image_path):
    if not BING_API_KEY:
        print(f"[!] Bing API key not provided. Skipping Bing search for {image_path}.")
        return []
    try:
        print(f"[INFO] Submitting to Bing Visual Search: {image_path}")
        with open(image_path, "rb") as f:
            files = {"image": (os.path.basename(image_path), f, "multipart/form-data")}
            headers = {
                "Ocp-Apim-Subscription-Key": BING_API_KEY
            }
            response = requests.post("https://api.bing.microsoft.com/v7.0/images/visualsearch", headers=headers, files=files)
        if response.status_code != 200:
            raise Exception(f"Bing API error: {response.text}")

        data = response.json()
        results = []
        tags = data.get("tags", [])
        for tag in tags:
            for action in tag.get("actions", []):
                if action.get("actionType") == "VisualSearch" and "data" in action:
                    for img in action["data"]:
                        results.append({
                            "title": img.get("name"),
                            "link": img.get("contentUrl"),
                            "source": img.get("hostPageDisplayUrl")
                        })
        return results

    except Exception as e:
        print(f"[ERROR] Bing reverse image search failed for {image_path}: {e}")
        return []

def save_results(image_name, engine, results):
    filename = os.path.join(OUTPUT_DIR, f"{image_name}_{engine}_results.json")
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Saved {engine} results to {filename}")

if __name__ == "__main__":
    image_files = [f for f in os.listdir(INPUT_IMAGE_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    for image_file in image_files:
        image_path = os.path.join(INPUT_IMAGE_DIR, image_file)
        base_name = os.path.splitext(image_file)[0]

        # Google Reverse Image Search via SerpAPI
        google_results = search_google_reverse(image_path)
        if google_results:
            save_results(base_name, "google", google_results)

        # TinEye stub
        tineye_results = search_tineye_stub(image_path)
        if tineye_results:
            save_results(base_name, "tineye", tineye_results)

        # Bing Visual Search
        bing_results = search_bing_visual(image_path)
        if bing_results:
            save_results(base_name, "bing", bing_results)
