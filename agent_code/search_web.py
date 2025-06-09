import exifread
from geopy.geocoders import Nominatim
import requests
from waybackpy import WaybackMachineCDXServerAPI
from newspaper import Article
import os
from serpapi import GoogleSearch
import snscrape.modules.reddit as reddit
from dotenv import load_dotenv
import subprocess
import re

load_dotenv()

# 1. Extract GPS from EXIF
def extract_gps(image_path):
    print(image_path)
    try:
        result = subprocess.run(["exiftool", image_path], capture_output=True, text=True)
        output = result.stdout

        lat = None
        lon = None

        for line in output.splitlines():
            if "GPS Latitude" in line and "Ref" not in line:
                lat_str = line.split(":")[1].strip()
                lat = convert_to_decimal(lat_str)
            elif "GPS Longitude" in line and "Ref" not in line:
                lon_str = line.split(":")[1].strip()
                lon = convert_to_decimal(lon_str)

        if lat is not None and lon is not None:
            return lat, lon
        else:
            return None
    except Exception as e:
        print(f"[ERROR] Failed to extract GPS: {e}")
        return None

def convert_to_decimal(coord_str):
    """
    Convert '37 deg 25' 19.20" N' to decimal degrees.
    """
    match = re.match(r"(\d+)\D+(\d+)\D+([\d.]+)", coord_str)
    if not match:
        return None
    degrees, minutes, seconds = map(float, match.groups())
    decimal = degrees + minutes / 60 + seconds / 3600
    if 'S' in coord_str or 'W' in coord_str:
        decimal = -decimal
    return decimal


# 2. Reverse geocode
def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.reverse((lat, lon), timeout=10)
    return location.address if location else None

# 3. SerpAPI search
def search_serpapi(query):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        print("[ERROR] Missing SerpAPI key.")
        return []

    params = {
        "q": query,
        "tbm": "nws",
        "api_key": api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return [item["link"] for item in results.get("news_results", [])]

# 4. Reddit fallback
# def search_reddit(query, max_results=5):
    # results = []
    # scraper = reddit.RedditSearchScraper(query)
    # for post in scraper.get_items():
        # results.append(post.url)
        # if len(results) >= max_results:
            # break
    # return results

# 5. Wayback Machine lookup
def find_archived_urls(query_url):
    cdx = WaybackMachineCDXServerAPI(query_url, user_agent="contextual-capture")
    return [page.archive_url for page in cdx.snapshots()]

# 6. Scrape news article
def scrape_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return {
        "title": article.title,
        "text": article.text,
        "top_image": article.top_image
    }

def infer_place_from_caption(caption):
    # Naive version – you can replace with NER or LLM call
    # You could also use spaCy NER to extract geopolitical entities
    keywords = ["DMZ", "North Korea", "Panmunjom", "Pyongyang", "Korean border", "Seoul", "checkpoint", "military base"]
    for keyword in keywords:
        if keyword.lower() in caption.lower():
            return keyword
    return None


# 7. Main logic
def main():
    image_path = "../photos/DG_DPRK_2015_009647.CR2"
    caption = "a person standing in front of a building"

    # Step 1: Extract GPS
    coords = extract_gps(image_path)
    if coords:
        lat, lon = coords
        print(f"[INFO] GPS: {lat}, {lon}")
        place = reverse_geocode(lat, lon)
    else:
        print("[WARN] No GPS data found. Inferring location from caption.")
        # Try to pull a keyword/place from the caption
    place = infer_place_from_caption(caption)

    if not place:
        print("[ERROR] Could not determine a location.")
        return
    print(f"[INFO] Using place: {place}")

    lat, lon = coords
    print(f"[INFO] GPS: {lat}, {lon}")

    # Step 2: Reverse geocode
    place = reverse_geocode(lat, lon)
    print(f"[INFO] Reverse geocoded to: {place}")

    # Step 3: Construct search query
    query = f'"{caption}" {place} 2020 site:reuters.com'
    print(f"[INFO] Query: {query}")

    # Step 4: Try SerpAPI
    urls = search_serpapi(query)
    # if not urls:
       #  print("[INFO] No SerpAPI results. Falling back to Reddit...")
        # urls = search_reddit(f"{caption} {place}")

    print(f"[INFO] Found {len(urls)} URLs")

    # Step 5: Scrape first article
    if urls:
        article_data = scrape_article(urls[0])
        print(f"\n[ARTICLE] {article_data['title']}\n\n{article_data['text'][:500]}...")

        # Step 6: Wayback Machine
        archived = find_archived_urls(urls[0])
        if archived:
            print(f"\n[ARCHIVED VERSIONS]\n" + "\n".join(archived[:3]))
    else:
        print("[INFO] No results found on any source.")

if __name__ == "__main__":
    main()
