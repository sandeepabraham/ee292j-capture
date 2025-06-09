import os
import json
import exifread
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# Setup paths
PHOTO_DIR = "../photos"
METADATA_DIR = "../metadata"

os.makedirs(METADATA_DIR, exist_ok=True)

# Load BLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

def generate_caption(image_path):
    raw_image = Image.open(image_path).convert('RGB')
    inputs = processor(images=raw_image, return_tensors="pt").to(device)
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

def extract_exif(image_path):
    exif_data = {}
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        for tag in tags:
            exif_data[tag] = str(tags[tag])
    return exif_data

def main():
    for filename in os.listdir(PHOTO_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(PHOTO_DIR, filename)
            print(f"Processing {filename}...")

            caption = generate_caption(img_path)
            exif = extract_exif(img_path)

            output = {
                "filename": filename,
                "caption": caption,
                "EXIF": exif
            }

            out_path = os.path.join(METADATA_DIR, f"{os.path.splitext(filename)[0]}.json")
            with open(out_path, "w") as f:
                json.dump(output, f, indent=2)

            print(f"Saved metadata to {out_path}")

if __name__ == "__main__":
    main()
