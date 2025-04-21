# filepath: generate_links.py
import chardet

base_url = "https://raw.githubusercontent.com/Rejserr/Shop/refs/heads/main/"

# Detect file encoding
with open("file_list.txt", "rb") as file:
    raw_data = file.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']

# Read the file with detected encoding
with open("file_list.txt", "r", encoding=encoding) as file:
    files = file.readlines()

# Write the links to a new file
with open("links.txt", "w", encoding="utf-8") as output:
    for file_path in files:
        file_path = file_path.strip()
        output.write(f"{base_url}{file_path}\n")