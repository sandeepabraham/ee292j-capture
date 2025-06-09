# ee292j-capture
Tools for contextualizing and enriching given image inputs with additional images

EE292J-Capture_Prototype_2025

by Sandeep Abraham and Karen Vo

This prototype currently looks for similar images based on detailed EXIF metadata provided in input images. It does not yet perform
reverse image searches consists of 3 tools that work in sequence:

1. exifsearch.py reads the exif metadata of all images stored in a designated
input folder, looks for descriptions, headlines, or captions and turns those into
unquoted queries on Google Images, storing all hits in json in exif_search_results.

2. download_newimages.py then uses the image links in the JSON results to download the images to a designated download folder. If
downloaded images' metadata contains location and date of capture, that is appended to the image's name for easy classification.

3. similarity_search.py then uses CLIP embeddings and cosine similarity to compare input images to downloaded images and groups all images
with a similarity score greater than 0.5 as high-fidelity similar images.

Future development of these tools includes auto-archiving website link results from exifsearch into wacz format via WebRecorder BrowserTrix, 
incorporating LLM API calls to interpret seed images and assess location to look for similar images online, and Bing/TinEye reverse image searching.
