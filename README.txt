EE292J-Capture_Prototype_2025

by Sandeep Abraham and Karen Vo

This prototype currently looks for similar images based on detailed EXIF metadata provided in input images. It does not yet perform
reverse image searches consists of 3 tools that work in sequence:

1. exifsearch.py reads the exif metadata of all images stored in a designated
input folder, looks for descriptions, headlines, or captions and turns those into
unquoted queries on Google Images, storing all hits in json in exif_search_results.

2. download_newimages.py then uses the image links
