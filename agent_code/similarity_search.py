import os
import json
import exiftool
import time
import shutil
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

TARGET_IMAGE = "./input_images/finalphoto1.jpg"
CANDIDATE_IMAGES_DIR = "./downloaded_images"
SIMILAR_IMAGES_DIR = "./downloaded_images/similar"
SIMILARITY_THRESHOLD = 0.3

DESCRIPTION_FIELDS = [
    "IPTC:Caption-Abstract",
    "IPTC:Headline",
    "EXIF:ImageDescription",
    "XMP:Description"
]

def extract_exif_description_fields(image_path):
    with exiftool.ExifTool() as et:
        raw_str = et.execute("-j", *[f"-{f}" for f in DESCRIPTION_FIELDS], image_path)
        metadata = json.loads(raw_str)[0] if isinstance(raw_str, bytes) else json.loads(raw_str)[0]

    fields = []
    for key in DESCRIPTION_FIELDS:
        val = metadata.get(key)
        if val:
            fields.append(val.lower())
    combined = " ".join(fields)
    print(f"[DEBUG] EXIF for {os.path.basename(image_path)}: {combined if combined else 'No valid fields found'}")
    return combined

def compute_similarity(text1, text2):
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    sim = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    return sim

def find_similar_images(target_image_path, candidate_dir):
    target_fields = extract_exif_description_fields(target_image_path)
    if not target_fields:
        print(f"[SKIP] No valid metadata in target image: {target_image_path}")
        return []

    similar_images = []
    for fname in os.listdir(candidate_dir):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        candidate_path = os.path.join(candidate_dir, fname)
        if candidate_path == target_image_path:
            continue

        candidate_fields = extract_exif_description_fields(candidate_path)
        if not candidate_fields:
            continue

        sim = compute_similarity(target_fields, candidate_fields)
        print(f"[DEBUG] Compared to {fname} → similarity: {sim:.2f}")
        if sim >= SIMILARITY_THRESHOLD:
            similar_images.append({
                "file": fname,
                "similarity": sim,
                "path": candidate_path,
                "candidate_fields": candidate_fields
            })

    return sorted(similar_images, key=lambda x: -x["similarity"])

if __name__ == "__main__":
    print("[INFO] Running similarity check")
    os.makedirs(SIMILAR_IMAGES_DIR, exist_ok=True)

    similar_images = find_similar_images(TARGET_IMAGE, CANDIDATE_IMAGES_DIR)

    if similar_images:
        print("\n[✓] Similar images found:")
        for img in similar_images:
            new_name = f"sim_{img['similarity']:.2f}_{img['file']}"
            destination = os.path.join(SIMILAR_IMAGES_DIR, new_name)
            shutil.copy2(img["path"], destination)
            print(f"- {img['file']} → {destination} (similarity: {img['similarity']:.2f})")
    else:
        print("\n[✗] No similar images found.")
