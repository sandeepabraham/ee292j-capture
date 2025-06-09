import requests
import os

BING_API_KEY = os.getenv("CysAAnuF7vnYL1Ux6NPlb9P5UNRHVJNrdhqPw8OT2FFMi7axuH2ZJQQJ99BFACYeBjFXJ3w3AAAEACOGx1EV")  # or hardcode your key
BING_ENDPOINT = "https://ee292j-search-api.cognitiveservices.azure.com/"

def search_bing_images(query, count=5):
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": count}
    response = requests.get(BING_ENDPOINT, headers=headers, params=params)
    response.raise_for_status()
    results = response.json()
    return [img["contentUrl"] for img in results.get("value", [])]

# Example:
if __name__ == "__main__":
    results = search_bing_images("North Korean border checkpoint")
    for i, url in enumerate(results):
        print(f"{i+1}: {url}")