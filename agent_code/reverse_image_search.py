import requests
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
if not SERPAPI_KEY:
    raise ValueError("Missing SerpAPI key. Check your .env file.")
IMAGE_URLS = {
    "finalphoto1.jpg": "https://drive.google.com/file/d/1SfP18JXS1Bhflaf5JhfLsO-NvXS5J0Bo/view?usp=sharing",
    "finalphoto2.JPG": "https://drive.google.com/file/d/1KATxGYpV9Tb3dyDYVy_kNo3St7lXjWlk/view?usp=sharing",
    "finalphoto3.JPG": "https://drive.google.com/file/d/13rSNaBJxDVcvMITyAD7C-U5QUhSa65Yu/view?usp=sharing"
}

def reverse_image_search(image_url):
    try:
        search_url = "https://serpapi.com/search"
        params = {
            "engine": "google_reverse_image",
            "image_url": image_url,
            "api_key": SERPAPI_KEY,
        }

        response = requests.get(search_url, params=params)
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response text (first 300 chars):\n{response.text[:300]}")

        data = response.json()
        results = []
        for res in data.get("image_results", []):
            results.append({
                "title": res.get("title"),
                "link": res.get("link"),
                "source": res.get("source")
            })
        return results

    except Exception as e:
        print(f"[EXCEPTION] Reverse search failed for URL {image_url}: {e}")
        return []

if __name__ == "__main__":
    output_dir = "../retrieved_media"
    os.makedirs(output_dir, exist_ok=True)

    for filename, image_url in IMAGE_URLS.items():
        print(f"[INFO] Searching for: {filename}")
        try:
            results = reverse_image_search(image_url)
            output_file = os.path.join(output_dir, f"{filename}_results.json")
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"[✓] Saved results to {output_file}")
        except Exception as e:
            print(f"[ERROR] Failed for {filename}: {e}")