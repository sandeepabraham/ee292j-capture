import os
import json
import requests
from dotenv import load_dotenv
import exiftool
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# Load environment variables
load_dotenv()

# Constants
INPUT_FOLDER = "./input_images"
OUTPUT_FOLDER = "./metadata"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load BLIP model for image captioning
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Priority EXIF fields to extract
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
                return str(value).strip(), normalized_metadata
        return None, normalized_metadata
    except Exception as e:
        print(f"[WARN] Failed to read EXIF from {image_path}: {e}")
        return None, {}

def generate_caption(image_path):
    raw_image = Image.open(image_path).convert("RGB")
    inputs = processor(raw_image, return_tensors="pt").to(device)
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

def main():
    for fname in os.listdir(INPUT_FOLDER):
        if not fname.lower().endswith((".jpg", ".jpeg")):
            continue

        image_path = os.path.join(INPUT_FOLDER, fname)
        print(f"[INFO] Processing {fname}")

        query, exif_data = extract_priority_metadata_fields(image_path)
        if not query:
            print(f"[INFO] No valid EXIF fields found in {fname}, generating caption instead...")
            try:
                query = generate_caption(image_path)
                print(f"[✓] Generated caption: {query}")
            except Exception as e:
                print(f"[ERROR] Failed to generate caption for {fname}: {e}")
                continue

        metadata_output = {
            "filename": fname,
            "caption": query,
            "EXIF": exif_data
        }

        out_path = os.path.join(OUTPUT_FOLDER, f"{fname}.json")
        with open(out_path, "w") as f:
            json.dump(metadata_output, f, indent=2)
        print(f"[✓] Saved metadata to {out_path}")

if __name__ == "__main__":
    main()
