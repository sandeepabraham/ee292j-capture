from serpapi import GoogleSearch
import os
import urllib.request


SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")  # or hardcode

def search_serpapi_images(query, num=5):
    params = {
        "engine": "google",
        "q": query,
        "tbm": "isch",  # image search
        "num": num,
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return [img["original"] for img in results.get("images_results", [])]

def download_images(urls, folder="bing_results"):
    os.makedirs(folder, exist_ok=True)
    for i, url in enumerate(urls):
        try:
            filename = os.path.join(folder, f"img_{i}.jpg")
            urllib.request.urlretrieve(url, filename)
        except Exception as e:
            print(f"Failed to download {url}: {e}")


# Example:
if __name__ == "__main__":
    images = search_serpapi_images("Panmunjom DMZ soldiers")
    for i, url in enumerate(images):
        print(f"{i+1}: {url}")