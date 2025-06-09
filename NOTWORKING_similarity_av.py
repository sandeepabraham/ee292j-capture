import os
import json
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

EXIF_SEARCH_FOLDER = "./exif_search_results"
SIMILARITY_OUTPUT_FOLDER = "./downloaded_media/similar_av"
THRESHOLD = 0.5  # adjust based on desired similarity

os.makedirs(SIMILARITY_OUTPUT_FOLDER, exist_ok=True)

def extract_titles_from_results(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return [entry.get("title", "") for entry in data.get("results", [])]
    except Exception as e:
        print(f"[ERROR] Failed to read {file_path}: {e}")
        return []

def compute_similarity_matrix(documents):
    vectorizer = TfidfVectorizer().fit_transform(documents)
    return cosine_similarity(vectorizer)

def find_similar_pairs(file_titles_map):
    file_names = list(file_titles_map.keys())
    all_titles = [" ".join(file_titles_map[f]) for f in file_names]
    similarity_matrix = compute_similarity_matrix(all_titles)

    similar_pairs = []
    for i in range(len(file_names)):
        for j in range(i + 1, len(file_names)):
            score = similarity_matrix[i][j]
            if score >= THRESHOLD:
                similar_pairs.append((file_names[i], file_names[j], score))
    return similar_pairs

def main():
    file_titles_map = {}
    for fname in os.listdir(EXIF_SEARCH_FOLDER):
        if not fname.endswith("av.json"):
            continue
        file_path = os.path.join(EXIF_SEARCH_FOLDER, fname)
        titles = extract_titles_from_results(file_path)
        if titles:
            file_titles_map[fname] = titles

    if not file_titles_map:
        print("[✗] No valid AV results found.")
        return

    print("[INFO] Running similarity check on AV results...")
    similar_pairs = find_similar_pairs(file_titles_map)

    for f1, f2, score in similar_pairs:
        print(f"[✓] Similar: {f1} <-> {f2} (Score: {score:.2f})")

if __name__ == "__main__":
    main()
